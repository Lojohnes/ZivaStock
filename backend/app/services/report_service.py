from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.count import FirstCount, SecondCount
from app.models.product import Product
from app.models.session import StocktakeSession
from app.models.user import User
from app.models.audit import AuditTrail
from app.models.location import Location, Shelf, ShelfSection
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class ReportService:
    """Thin wrapper over the reporting VIEWs defined in
    database/migrations/V009__views.sql — all heavy aggregation happens in
    Postgres rather than in application code."""

    def __init__(self, db: Session):
        self.db = db

    def generate_variance_report(self, session_id: int) -> Dict:
        """Wraps v_product_variance — per-session, per-product reconciliation."""
        session = self.db.query(StocktakeSession).filter(StocktakeSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found")

        # Build the report directly from synchronized counts. The historical
        # database view only contains rows after adjustments are posted, which
        # made valid mobile counts invisible in backoffice reports.
        rows = self.db.execute(text("""
            SELECT p.id AS product_id, p.barcode, p.description,
                   p.unit_of_measure, p.system_quantity, p.unit_cost,
                   COALESCE(SUM(fc.quantity), 0) AS first_count_quantity,
                   COALESCE(SUM(sc.quantity), 0) AS second_count_quantity
            FROM products p
            LEFT JOIN first_counts fc ON fc.product_id = p.id AND fc.session_id = :session_id
            LEFT JOIN second_counts sc ON sc.product_id = p.id AND sc.session_id = :session_id
            WHERE p.is_active = TRUE
            GROUP BY p.id, p.barcode, p.description, p.unit_of_measure, p.system_quantity
            ORDER BY p.id
        """), {"session_id": session_id}).mappings().all()

        variances = []
        for row in rows:
            item = dict(row)
            first_qty = float(item.pop("first_count_quantity") or 0)
            second_qty = float(item.pop("second_count_quantity") or 0)
            counted_qty = second_qty if second_qty else first_qty
            system_qty = float(item.get("system_quantity") or 0)
            unit_cost = float(item.get("unit_cost") or 0)
            item.update({
                "first_count_quantity": first_qty,
                "second_count_quantity": second_qty,
                "final_quantity": counted_qty,
                "variance_quantity": counted_qty - system_qty,
                "variance_value": (counted_qty - system_qty) * unit_cost,
                "adjustment_type": None,
                "adjustment_status": None,
            })
            variances.append(item)
        overcount = len([v for v in variances if (v["variance_quantity"] or 0) > 0])
        undercount = len([v for v in variances if (v["variance_quantity"] or 0) < 0])
        accurate = len([v for v in variances if (v["variance_quantity"] or 0) == 0])
        total_variance_value = sum((v["variance_value"] or 0) for v in variances)

        return {
            "session_id": session_id,
            "session_name": session.name,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_products": len(variances),
                "total_variance_value": float(total_variance_value),
                "overcount_count": overcount,
                "undercount_count": undercount,
                "accurate_count": accurate,
            },
            "variances": variances,
        }

    def generate_duplicate_report(self, session_id: int) -> Dict:
        """List products with multiple count submissions in a session."""
        session = self.db.query(StocktakeSession).filter(StocktakeSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found")
        rows = self.db.execute(text("""
            SELECT p.barcode, p.product_code, p.description,
                   COUNT(fc.id) AS first_count_entries,
                   COUNT(sc.id) AS second_count_entries
            FROM products p
            LEFT JOIN first_counts fc ON fc.product_id = p.id AND fc.session_id = :session_id
            LEFT JOIN second_counts sc ON sc.product_id = p.id AND sc.session_id = :session_id
            GROUP BY p.id, p.barcode, p.product_code, p.description
            HAVING COUNT(fc.id) > 1 OR COUNT(sc.id) > 1
            ORDER BY p.description
        """), {"session_id": session_id}).mappings().all()
        return {
            "session_id": session_id,
            "session_name": session.name,
            "generated_at": datetime.utcnow().isoformat(),
            "duplicates": [dict(row) for row in rows],
        }

    def generate_missing_stock_report(self, session_id: int) -> Dict:
        """Products in the system with no first_count row in this session."""
        session = self.db.query(StocktakeSession).filter(StocktakeSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found")

        all_products = self.db.query(Product).filter(Product.is_active == True).all()
        counted_ids = {
            pid for (pid,) in self.db.query(FirstCount.product_id)
            .filter(FirstCount.session_id == session_id)
            .distinct()
            .all()
        }

        missing = [
            {
                "product": {
                    "id": p.id,
                    "barcode": p.barcode,
                    "product_code": p.product_code,
                    "description": p.description,
                },
                "system_quantity": float(p.system_quantity),
            }
            for p in all_products
            if p.id not in counted_ids
        ]

        return {
            "session_id": session_id,
            "total_products": len(all_products),
            "counted_products": len(counted_ids),
            "missing_products": len(missing),
            "missing": missing,
        }

    def generate_user_productivity_report(self, session_id: Optional[int] = None) -> Dict:
        """Wraps v_user_productivity, optionally scoped by counting activity
        within a session (post-filtered since the view is global)."""
        rows = self.db.execute(text("SELECT * FROM v_user_productivity")).mappings().all()
        users_data = [dict(r) for r in rows if r["first_counts_submitted"] or r["second_counts_submitted"]]
        return {"session_id": session_id, "users": users_data}

    def generate_audit_report(
        self,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """Query the partitioned audit_trail table directly (partition pruning
        applies automatically when created_at bounds are supplied)."""
        query = self.db.query(AuditTrail)

        if user_id:
            query = query.filter(AuditTrail.user_id == user_id)
        if start_date:
            query = query.filter(AuditTrail.created_at >= start_date)
        if end_date:
            query = query.filter(AuditTrail.created_at <= end_date)

        audit_logs = query.order_by(AuditTrail.created_at.desc()).limit(1000).all()

        actions = []
        for log in audit_logs:
            user = self.db.query(User).filter(User.id == log.user_id).first()
            actions.append({
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                } if user else None,
                "ip_address": str(log.ip_address) if log.ip_address else None,
                "created_at": log.created_at.isoformat(),
            })

        return {
            "user_id": user_id,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "total_actions": len(actions),
            "actions": actions,
        }

    def get_session_progress(self, session_id: Optional[int] = None) -> List[Dict]:
        """Wraps v_session_progress."""
        if session_id:
            rows = self.db.execute(
                text("SELECT * FROM v_session_progress WHERE session_id = :session_id"),
                {"session_id": session_id},
            ).mappings().all()
        else:
            rows = self.db.execute(
                text("SELECT * FROM v_session_progress ORDER BY session_id DESC LIMIT 20")
            ).mappings().all()
        return [dict(r) for r in rows]

    def get_dashboard_stats(self) -> Dict:
        """High-level dashboard analytics, backed by v_session_progress for the
        per-session breakdown."""
        total_sessions = self.db.query(StocktakeSession).count()
        active_sessions = self.db.query(StocktakeSession).filter(
            StocktakeSession.status == 'in_progress'
        ).count()
        completed_sessions = self.db.query(StocktakeSession).filter(
            StocktakeSession.status == 'completed'
        ).count()

        total_products = self.db.query(Product).count()
        total_first_counts = self.db.query(FirstCount).count()
        total_second_counts = self.db.query(SecondCount).count()
        total_users = self.db.query(User).count()

        total_sections = self.db.query(ShelfSection).count()
        counted_sections = self.db.query(FirstCount.shelf_section_id).distinct().count()

        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_counts = (
            self.db.query(FirstCount).filter(FirstCount.counted_at >= last_24h).count()
            + self.db.query(SecondCount).filter(SecondCount.counted_at >= last_24h).count()
        )

        session_progress = self.get_session_progress()

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "completed_sessions": completed_sessions,
                "total_products": total_products,
                "total_first_counts": total_first_counts,
                "total_second_counts": total_second_counts,
                "total_users": total_users,
                "total_sections": total_sections,
                "counted_sections": counted_sections,
                "section_completion_percentage": round(
                    (counted_sections / total_sections * 100), 2
                ) if total_sections > 0 else 0,
                "recent_counts_24h": recent_counts,
            },
            "sessions": session_progress[:10],
        }
