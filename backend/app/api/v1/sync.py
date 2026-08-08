from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.schemas.sync import SyncPushRequest, SyncPushResponse, SyncPullResponse, SyncStatusResponse, SyncQueueResponse
from app.services.sync_service import SyncService
from app.api.deps import get_current_user_id, get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/push", response_model=SyncPushResponse, status_code=status.HTTP_201_CREATED)
def push_items(
    sync_data: SyncPushRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Push a batch of offline-generated first/second counts from mobile to
    the server. Idempotent per (user, client_id)."""
    sync_service = SyncService(db)
    return sync_service.push_items(current_user.id, sync_data)


@router.get("/pull", response_model=SyncPullResponse)
def pull_data(
    last_sync: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Pull latest products/shelf sections + this user's own counts changed
    since last_sync, for mobile offline caching."""
    sync_service = SyncService(db)
    return sync_service.pull_data(current_user.id, last_sync)


@router.get("/status", response_model=SyncStatusResponse)
def get_sync_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get sync queue status for current user"""
    sync_service = SyncService(db)
    return sync_service.get_sync_status(current_user.id)


@router.get("/queue", response_model=List[SyncQueueResponse])
def get_queue_items(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List this user's sync queue items, optionally filtered by status"""
    return SyncService(db).get_queue_items(current_user.id, status=status_filter)


@router.post("/retry")
def retry_failed(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Re-attempt all failed items in this user's sync queue"""
    retried = SyncService(db).retry_failed(current_user.id)
    return {"retried": retried}
