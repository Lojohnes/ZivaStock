from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.adjustment import Adjustment
from typing import Optional, List
from datetime import datetime


class AdjustmentService:
    """Wraps the reconciliation SQL functions defined in
    database/migrations/V010__functions_and_procedures.sql, plus CRUD/approval
    workflow for individual adjustment rows."""

    def __init__(self, db: Session):
        self.db = db

    def get_adjustment(self, adjustment_id: int) -> Optional[Adjustment]:
        return self.db.query(Adjustment).filter(Adjustment.id == adjustment_id).first()

    def get_adjustments(
        self,
        skip: int = 0,
        limit: int = 50,
        session_id: Optional[int] = None,
        status: Optional[str] = None,
        adjustment_type: Optional[str] = None,
    ) -> tuple[List[Adjustment], int]:
        query = self.db.query(Adjustment)
        if session_id:
            query = query.filter(Adjustment.session_id == session_id)
        if status:
            query = query.filter(Adjustment.status == status)
        if adjustment_type:
            query = query.filter(Adjustment.adjustment_type == adjustment_type)

        total = query.count()
        items = query.order_by(Adjustment.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def generate_adjustments(self, session_id: int, actor_id: int) -> int:
        """Calls fn_generate_adjustments() — upserts one adjustment row per
        (product, shelf_section) scope, reconciling first/second counts against
        system_quantity."""
        result = self.db.execute(
            text("SELECT fn_generate_adjustments(:session_id, :actor_id) AS affected"),
            {"session_id": session_id, "actor_id": actor_id},
        )
        self.db.commit()
        row = result.first()
        return row.affected if row else 0

    def get_session_variance(self, session_id: int) -> dict:
        """Calls fn_calculate_session_variance() for a summary of the session's
        reconciliation outcome."""
        result = self.db.execute(
            text("SELECT * FROM fn_calculate_session_variance(:session_id)"),
            {"session_id": session_id},
        )
        row = result.mappings().first()
        return dict(row) if row else {}

    def get_discrepancies(self, session_id: int, tolerance_pct: float = 0) -> List[dict]:
        """Calls fn_detect_count_discrepancy() to list first/second count
        mismatches beyond the given tolerance percentage, before adjustments
        are generated."""
        result = self.db.execute(
            text("SELECT * FROM fn_detect_count_discrepancy(:session_id, :tolerance_pct)"),
            {"session_id": session_id, "tolerance_pct": tolerance_pct},
        )
        return [dict(row) for row in result.mappings().all()]

    def approve_adjustment(self, adjustment_id: int, approved_by: int) -> Optional[Adjustment]:
        adjustment = self.get_adjustment(adjustment_id)
        if not adjustment:
            return None
        if adjustment.status != "pending":
            raise ValueError(f"Adjustment must be 'pending' to approve (currently '{adjustment.status}')")
        adjustment.status = "approved"
        adjustment.approved_by = approved_by
        adjustment.approved_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(adjustment)
        return adjustment

    def reject_adjustment(self, adjustment_id: int, approved_by: int, reason: Optional[str] = None) -> Optional[Adjustment]:
        adjustment = self.get_adjustment(adjustment_id)
        if not adjustment:
            return None
        if adjustment.status != "pending":
            raise ValueError(f"Adjustment must be 'pending' to reject (currently '{adjustment.status}')")
        adjustment.status = "rejected"
        adjustment.approved_by = approved_by
        adjustment.approved_at = datetime.utcnow()
        if reason:
            adjustment.reason = reason
        self.db.commit()
        self.db.refresh(adjustment)
        return adjustment

    def post_adjustment(self, adjustment_id: int) -> Optional[Adjustment]:
        """Post an approved adjustment (applies it to inventory). Actual
        `products.system_quantity` mutation would be handled by a follow-up
        inventory-sync job; here we just mark it posted."""
        adjustment = self.get_adjustment(adjustment_id)
        if not adjustment:
            return None
        if adjustment.status != "approved":
            raise ValueError(f"Adjustment must be 'approved' to post (currently '{adjustment.status}')")
        adjustment.status = "posted"
        adjustment.posted_at = datetime.utcnow()

        from app.models.product import Product
        product = self.db.query(Product).filter(Product.id == adjustment.product_id).first()
        if product:
            product.system_quantity = adjustment.final_quantity

        self.db.commit()
        self.db.refresh(adjustment)
        return adjustment

    def close_session(self, session_id: int, actor_id: int) -> bool:
        """Calls fn_close_stocktake_session(): generates adjustments and marks
        the session 'completed' in a single DB transaction."""
        result = self.db.execute(
            text("SELECT fn_close_stocktake_session(:session_id, :actor_id) AS ok"),
            {"session_id": session_id, "actor_id": actor_id},
        )
        self.db.commit()
        row = result.first()
        return bool(row.ok) if row else False
