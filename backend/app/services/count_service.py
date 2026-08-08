from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.count import FirstCount, SecondCount
from app.models.product import Product
from app.models.location import ShelfSection
from app.schemas.count import FirstCountCreate, SecondCountCreate, CountUpdate
from typing import Optional, List, Tuple
from datetime import datetime


class CountService:
    """Manages independent first/second counts. Consolidation-on-conflict
    (same session/product/shelf_section/user) mirrors the DB's unique
    constraints (`uq_first_count_scope` / `uq_second_count_scope`); segregation
    of duties for second counts is enforced by the DB trigger
    `trg_prevent_same_user_second_count` and surfaced here as a ValueError."""

    def __init__(self, db: Session):
        self.db = db

    def _verify_scope(self, product_id: int, shelf_section_id: int):
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
        section = self.db.query(ShelfSection).filter(ShelfSection.id == shelf_section_id).first()
        if not section:
            raise ValueError("Shelf section not found")

    # -------------------------------------------------------------------
    # First Counts
    # -------------------------------------------------------------------

    def get_first_count(self, count_id: int) -> Optional[FirstCount]:
        return self.db.query(FirstCount).filter(FirstCount.id == count_id).first()

    def get_first_counts(
        self,
        skip: int = 0,
        limit: int = 50,
        session_id: Optional[int] = None,
        shelf_section_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Tuple[List[FirstCount], int]:
        query = self.db.query(FirstCount)
        if session_id:
            query = query.filter(FirstCount.session_id == session_id)
        if shelf_section_id:
            query = query.filter(FirstCount.shelf_section_id == shelf_section_id)
        if user_id:
            query = query.filter(FirstCount.user_id == user_id)

        total = query.count()
        items = query.order_by(FirstCount.counted_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def create_first_count(self, count_data: FirstCountCreate, user_id: int) -> FirstCount:
        """Create (or consolidate, i.e. overwrite quantity for) a first count
        within the unique (session, product, shelf_section, user) scope."""
        self._verify_scope(count_data.product_id, count_data.shelf_section_id)

        existing = self.db.query(FirstCount).filter(
            FirstCount.session_id == count_data.session_id,
            FirstCount.product_id == count_data.product_id,
            FirstCount.shelf_section_id == count_data.shelf_section_id,
            FirstCount.user_id == user_id,
        ).first()

        if existing:
            existing.quantity = count_data.quantity
            existing.counted_at = datetime.utcnow()
            existing.source = count_data.source
            self.db.commit()
            self.db.refresh(existing)
            return existing

        db_count = FirstCount(**count_data.model_dump(), user_id=user_id)
        self.db.add(db_count)
        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Could not save first count: {e.orig}") from e
        self.db.refresh(db_count)
        return db_count

    def update_first_count(self, count_id: int, count_data: CountUpdate) -> Optional[FirstCount]:
        count = self.get_first_count(count_id)
        if not count:
            return None
        for field, value in count_data.model_dump(exclude_unset=True).items():
            setattr(count, field, value)
        self.db.commit()
        self.db.refresh(count)
        return count

    def delete_first_count(self, count_id: int) -> bool:
        count = self.get_first_count(count_id)
        if not count:
            return False
        self.db.delete(count)
        self.db.commit()
        return True

    # -------------------------------------------------------------------
    # Second Counts
    # -------------------------------------------------------------------

    def get_second_count(self, count_id: int) -> Optional[SecondCount]:
        return self.db.query(SecondCount).filter(SecondCount.id == count_id).first()

    def get_second_counts(
        self,
        skip: int = 0,
        limit: int = 50,
        session_id: Optional[int] = None,
        shelf_section_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Tuple[List[SecondCount], int]:
        query = self.db.query(SecondCount)
        if session_id:
            query = query.filter(SecondCount.session_id == session_id)
        if shelf_section_id:
            query = query.filter(SecondCount.shelf_section_id == shelf_section_id)
        if user_id:
            query = query.filter(SecondCount.user_id == user_id)

        total = query.count()
        items = query.order_by(SecondCount.counted_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def create_second_count(self, count_data: SecondCountCreate, user_id: int) -> SecondCount:
        """Create (or consolidate) a second count. Rejects the write if the
        submitting user already performed the linked first count (segregation
        of duties), whether caught here or by the DB trigger."""
        self._verify_scope(count_data.product_id, count_data.shelf_section_id)

        if count_data.first_count_id:
            first_count = self.get_first_count(count_data.first_count_id)
            if first_count and first_count.user_id == user_id:
                raise ValueError(
                    "Segregation of duties violation: you cannot perform the second count "
                    "for a product/section you already first-counted."
                )

        existing = self.db.query(SecondCount).filter(
            SecondCount.session_id == count_data.session_id,
            SecondCount.product_id == count_data.product_id,
            SecondCount.shelf_section_id == count_data.shelf_section_id,
            SecondCount.user_id == user_id,
        ).first()

        if existing:
            existing.quantity = count_data.quantity
            existing.counted_at = datetime.utcnow()
            existing.source = count_data.source
            self.db.commit()
            self.db.refresh(existing)
            return existing

        db_count = SecondCount(**count_data.model_dump(), user_id=user_id)
        self.db.add(db_count)
        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Could not save second count: {e.orig}") from e
        self.db.refresh(db_count)
        return db_count

    def update_second_count(self, count_id: int, count_data: CountUpdate) -> Optional[SecondCount]:
        count = self.get_second_count(count_id)
        if not count:
            return None
        for field, value in count_data.model_dump(exclude_unset=True).items():
            setattr(count, field, value)
        self.db.commit()
        self.db.refresh(count)
        return count

    def delete_second_count(self, count_id: int) -> bool:
        count = self.get_second_count(count_id)
        if not count:
            return False
        self.db.delete(count)
        self.db.commit()
        return True
