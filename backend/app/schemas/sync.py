from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class SyncQueueItemCreate(BaseModel):
    """A single offline-generated mutation. `client_id` is a mobile-generated
    idempotency key unique per (user, client_id) — replays are safe."""
    device_id: Optional[str] = None
    entity_type: str = Field(..., pattern="^(first_count|second_count)$")
    entity_id: Optional[int] = None
    client_id: str
    action: str = Field(..., pattern="^(create|update|delete)$")
    payload: dict


class SyncPushRequest(BaseModel):
    items: List[SyncQueueItemCreate]


class SyncPushResultItem(BaseModel):
    client_id: str
    status: str
    error: Optional[str] = None


class SyncPushResponse(BaseModel):
    success_count: int
    failed_count: int
    results: List[SyncPushResultItem]


class SyncPullResponse(BaseModel):
    products: List[dict]
    first_counts: List[dict]
    second_counts: List[dict]
    shelf_sections: List[dict]
    sync_timestamp: datetime


class SyncStatusResponse(BaseModel):
    pending_sync_count: int
    failed_sync_count: int
    last_sync_at: Optional[datetime]
    sync_status: str


class SyncQueueResponse(BaseModel):
    id: int
    user_id: int
    device_id: Optional[str]
    entity_type: str
    entity_id: Optional[int]
    client_id: str
    action: str
    status: str
    retry_count: int
    error_message: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True
