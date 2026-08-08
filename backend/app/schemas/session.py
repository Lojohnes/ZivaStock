from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class SessionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    location_id: int
    session_type: str = Field("full", pattern="^(full|cycle|spot_check)$")


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    session_type: Optional[str] = Field(None, pattern="^(full|cycle|spot_check)$")


class SessionResponse(BaseModel):
    id: int
    uuid: UUID
    name: str
    description: Optional[str]
    location_id: int
    session_type: str
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    created_by: int
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionWithDetails(SessionResponse):
    location: Optional["LocationResponse"] = None
    creator: Optional["UserResponse"] = None


class SessionAssignmentBase(BaseModel):
    user_id: int
    shelf_section_id: Optional[int] = None
    assignment_role: str = Field("first_counter", pattern="^(first_counter|second_counter|supervisor|reconciler)$")


class SessionAssignmentCreate(SessionAssignmentBase):
    pass


class SessionAssignmentResponse(BaseModel):
    id: int
    session_id: int
    user_id: int
    shelf_section_id: Optional[int]
    assignment_role: str
    status: str
    assigned_by: Optional[int]
    assigned_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class SessionAssignmentWithUser(SessionAssignmentResponse):
    user: Optional["UserResponse"] = None


# Forward references
from app.schemas.location import LocationResponse
from app.schemas.user import UserResponse
SessionWithDetails.model_rebuild()
SessionAssignmentWithUser.model_rebuild()
