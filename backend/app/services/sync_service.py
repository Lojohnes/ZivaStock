from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.sync import SyncQueue
from app.models.product import Product
from app.models.count import FirstCount, SecondCount
from app.models.location import ShelfSection
from app.schemas.sync import SyncPushRequest, SyncPushResponse, SyncPushResultItem
from app.schemas.count import FirstCountCreate, SecondCountCreate
from app.services.count_service import CountService
from typing import List, Optional
from datetime import datetime, timedelta


class SyncService:
    """Idempotent offline-sync ingestion. Each pushed item is first persisted
    to `sync_queue` (so nothing is lost even if processing fails), then
    applied via CountService, then marked completed/failed on the queue row."""

    def __init__(self, db: Session):
        self.db = db

    def push_items(self, user_id: int, sync_data: SyncPushRequest) -> SyncPushResponse:
        count_service = CountService(self.db)
        results: List[SyncPushResultItem] = []
        success_count = 0
        failed_count = 0

        for item in sync_data.items:
            # Idempotency: if this (user, client_id) was already processed, short-circuit
            queue_row = self.db.query(SyncQueue).filter(
                SyncQueue.user_id == user_id,
                SyncQueue.client_id == item.client_id,
            ).first()

            if queue_row and queue_row.status == "completed":
                results.append(SyncPushResultItem(client_id=item.client_id, status="already_processed"))
                success_count += 1
                continue

            if not queue_row:
                queue_row = SyncQueue(
                    user_id=user_id,
                    device_id=item.device_id,
                    entity_type=item.entity_type,
                    entity_id=item.entity_id,
                    client_id=item.client_id,
                    action=item.action,
                    payload=item.payload,
                    status="processing",
                )
                self.db.add(queue_row)
                self.db.commit()
                self.db.refresh(queue_row)

            try:
                self._apply_item(user_id, item.entity_type, item.action, item.payload)
                queue_row.status = "completed"
                queue_row.processed_at = datetime.utcnow()
                self.db.commit()
                results.append(SyncPushResultItem(client_id=item.client_id, status="completed"))
                success_count += 1
            except Exception as e:
                self.db.rollback()
                queue_row.status = "failed"
                queue_row.retry_count = (queue_row.retry_count or 0) + 1
                queue_row.error_message = str(e)
                queue_row.last_attempt_at = datetime.utcnow()
                self.db.commit()
                results.append(SyncPushResultItem(client_id=item.client_id, status="failed", error=str(e)))
                failed_count += 1

        return SyncPushResponse(success_count=success_count, failed_count=failed_count, results=results)

    def _apply_item(self, user_id: int, entity_type: str, action: str, payload: dict):
        count_service = CountService(self.db)
        if entity_type == "first_count":
            if action in ("create", "update"):
                data = FirstCountCreate(**payload)
                count_service.create_first_count(data, user_id)
            elif action == "delete" and payload.get("id"):
                count_service.delete_first_count(payload["id"])
        elif entity_type == "second_count":
            if action in ("create", "update"):
                data = SecondCountCreate(**payload)
                count_service.create_second_count(data, user_id)
            elif action == "delete" and payload.get("id"):
                count_service.delete_second_count(payload["id"])
        else:
            raise ValueError(f"Unsupported entity_type: {entity_type}")

    def pull_data(self, user_id: int, last_sync: Optional[datetime] = None) -> dict:
        """Pull latest master/reference data + this user's own counts changed
        since last_sync, for mobile offline caching."""
        if last_sync is None:
            last_sync = datetime.utcnow() - timedelta(days=30)

        products = self.db.query(Product).filter(Product.updated_at >= last_sync).all()
        first_counts = self.db.query(FirstCount).filter(
            FirstCount.user_id == user_id, FirstCount.counted_at >= last_sync
        ).all()
        second_counts = self.db.query(SecondCount).filter(
            SecondCount.user_id == user_id, SecondCount.counted_at >= last_sync
        ).all()
        shelf_sections = self.db.query(ShelfSection).filter(ShelfSection.updated_at >= last_sync).all()

        return {
            "products": [
                {
                    "id": p.id,
                    "sku": p.sku,
                    "barcode": p.barcode,
                    "product_code": p.product_code,
                    "description": p.description,
                    "unit_of_measure": p.unit_of_measure,
                    "system_quantity": float(p.system_quantity),
                    "unit_cost": float(p.unit_cost),
                    "updated_at": p.updated_at.isoformat(),
                }
                for p in products
            ],
            "first_counts": [
                {
                    "id": c.id,
                    "session_id": c.session_id,
                    "product_id": c.product_id,
                    "shelf_section_id": c.shelf_section_id,
                    "file_number": c.file_number,
                    "section_number": c.section_number,
                    "quantity": float(c.quantity),
                    "counted_at": c.counted_at.isoformat(),
                }
                for c in first_counts
            ],
            "second_counts": [
                {
                    "id": c.id,
                    "session_id": c.session_id,
                    "product_id": c.product_id,
                    "shelf_section_id": c.shelf_section_id,
                    "file_number": c.file_number,
                    "section_number": c.section_number,
                    "quantity": float(c.quantity),
                    "counted_at": c.counted_at.isoformat(),
                }
                for c in second_counts
            ],
            "shelf_sections": [
                {
                    "id": s.id,
                    "shelf_id": s.shelf_id,
                    "name": s.name,
                    "description": s.description,
                    "updated_at": s.updated_at.isoformat(),
                }
                for s in shelf_sections
            ],
            "sync_timestamp": datetime.utcnow().isoformat(),
        }

    def get_sync_status(self, user_id: int) -> dict:
        """Get sync queue status for user"""
        pending_count = self.db.query(SyncQueue).filter(
            SyncQueue.user_id == user_id, SyncQueue.status == "pending"
        ).count()
        failed_count = self.db.query(SyncQueue).filter(
            SyncQueue.user_id == user_id, SyncQueue.status == "failed"
        ).count()

        last_completed = self.db.query(SyncQueue).filter(
            SyncQueue.user_id == user_id, SyncQueue.status == "completed"
        ).order_by(SyncQueue.processed_at.desc()).first()

        return {
            "pending_sync_count": pending_count,
            "failed_sync_count": failed_count,
            "last_sync_at": last_completed.processed_at if last_completed else None,
            "sync_status": "up_to_date" if pending_count == 0 and failed_count == 0 else "pending",
        }

    def get_queue_items(self, user_id: int, status: Optional[str] = None) -> List[SyncQueue]:
        query = self.db.query(SyncQueue).filter(SyncQueue.user_id == user_id)
        if status:
            query = query.filter(SyncQueue.status == status)
        return query.order_by(SyncQueue.created_at.desc()).all()

    def retry_failed(self, user_id: int) -> int:
        """Re-attempt all failed items in this user's sync queue"""
        failed_items = self.db.query(SyncQueue).filter(
            SyncQueue.user_id == user_id, SyncQueue.status == "failed"
        ).all()

        retried = 0
        for item in failed_items:
            try:
                self._apply_item(user_id, item.entity_type, item.action, item.payload)
                item.status = "completed"
                item.processed_at = datetime.utcnow()
                self.db.commit()
                retried += 1
            except Exception as e:
                self.db.rollback()
                item.retry_count = (item.retry_count or 0) + 1
                item.error_message = str(e)
                item.last_attempt_at = datetime.utcnow()
                self.db.commit()

        return retried
