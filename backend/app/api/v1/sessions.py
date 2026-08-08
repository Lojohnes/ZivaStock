from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.schemas.session import (
    SessionCreate, SessionUpdate, SessionResponse, SessionWithDetails,
    SessionAssignmentCreate, SessionAssignmentResponse, SessionAssignmentWithUser,
)
from app.schemas.location import ShelfSectionResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.session_service import SessionService
from app.models.session import StocktakeSession
from app.models.user import User
from app.api.deps import get_current_user_id, get_current_user, require_permission

router = APIRouter()


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("sessions.create")),
):
    """Create a new stocktake session (requires sessions.create permission)"""
    session_service = SessionService(db)
    try:
        session = session_service.create_session(session_data, current_user.id)
        return session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=PaginatedResponse[SessionResponse])
def get_sessions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    location_id: Optional[int] = None,
    session_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get sessions with pagination and filters"""
    session_service = SessionService(db)
    skip = (page - 1) * limit
    sessions, total = session_service.get_sessions(skip=skip, limit=limit, status=status, location_id=location_id, session_type=session_type)
    pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        items=sessions,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get("/{session_id}", response_model=SessionWithDetails)
def get_session(session_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """Get session by ID with details"""
    session_service = SessionService(db)
    session = session_service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    from app.models.location import Location

    location = db.query(Location).filter(Location.id == session.location_id).first()
    creator = db.query(User).filter(User.id == session.created_by).first()

    return SessionWithDetails(
        id=session.id,
        uuid=session.uuid,
        name=session.name,
        description=session.description,
        location_id=session.location_id,
        session_type=session.session_type,
        status=session.status,
        start_time=session.start_time,
        end_time=session.end_time,
        created_by=session.created_by,
        approved_by=session.approved_by,
        approved_at=session.approved_at,
        created_at=session.created_at,
        updated_at=session.updated_at,
        location=location,
        creator=creator,
    )


@router.get("/{session_id}/sections", response_model=List[ShelfSectionResponse])
def get_session_sections(session_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """Get shelf sections for the location of a session"""
    session_service = SessionService(db)
    sections = session_service.get_session_sections(session_id)
    return sections


@router.put("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    session_data: SessionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("sessions.update")),
):
    """Update session (requires sessions.update permission)"""
    session_service = SessionService(db)
    session = session_service.update_session(session_id, session_data)
    
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    return session


@router.post("/{session_id}/start", response_model=SessionResponse)
def start_session(
    session_id: int, db: Session = Depends(get_db),
    _: User = Depends(require_permission("sessions.update")),
):
    """Start a session (not_started -> in_progress)"""
    session_service = SessionService(db)
    try:
        session = session_service.start_session(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{session_id}/pause", response_model=SessionResponse)
def pause_session(
    session_id: int, db: Session = Depends(get_db),
    _: User = Depends(require_permission("sessions.update")),
):
    """Pause a session (in_progress -> paused)"""
    session_service = SessionService(db)
    try:
        session = session_service.pause_session(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{session_id}/resume", response_model=SessionResponse)
def resume_session(
    session_id: int, db: Session = Depends(get_db),
    _: User = Depends(require_permission("sessions.update")),
):
    """Resume a session (paused -> in_progress)"""
    session_service = SessionService(db)
    try:
        session = session_service.resume_session(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{session_id}/counting-complete", response_model=SessionResponse)
def mark_counting_complete(
    session_id: int, db: Session = Depends(get_db),
    _: User = Depends(require_permission("sessions.update")),
):
    """Mark counting complete (in_progress -> counting_complete)"""
    session_service = SessionService(db)
    try:
        session = session_service.mark_counting_complete(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{session_id}/reconcile", response_model=SessionResponse)
def start_reconciling(
    session_id: int, db: Session = Depends(get_db),
    _: User = Depends(require_permission("sessions.reconcile")),
):
    """Start reconciliation (counting_complete -> reconciling)"""
    session_service = SessionService(db)
    try:
        session = session_service.start_reconciling(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{session_id}/complete", response_model=SessionResponse)
def complete_session(
    session_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("sessions.approve")),
):
    """Complete and approve a session (reconciling -> completed)"""
    session_service = SessionService(db)
    try:
        session = session_service.complete_session(session_id, approved_by=current_user.id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{session_id}/archive", response_model=SessionResponse)
def archive_session(
    session_id: int, db: Session = Depends(get_db),
    _: User = Depends(require_permission("sessions.update")),
):
    """Archive a session (completed -> archived)"""
    session_service = SessionService(db)
    try:
        session = session_service.archive_session(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{session_id}/cancel", response_model=SessionResponse)
def cancel_session(
    session_id: int, db: Session = Depends(get_db),
    _: User = Depends(require_permission("sessions.update")),
):
    """Cancel a session"""
    session_service = SessionService(db)
    try:
        session = session_service.cancel_session(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{session_id}/assignments", response_model=List[SessionAssignmentWithUser])
def get_session_assignments(session_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """Get all assignments for a session"""
    return SessionService(db).get_session_assignments(session_id)


@router.post("/{session_id}/assignments", response_model=SessionAssignmentResponse, status_code=status.HTTP_201_CREATED)
def assign_user(
    session_id: int,
    assignment_data: SessionAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("sessions.assign")),
):
    """Assign a user to a session (requires sessions.assign permission)"""
    session_service = SessionService(db)
    assignment = session_service.assign_user(session_id, assignment_data, assigned_by=current_user.id)
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return assignment


@router.delete("/assignments/{assignment_id}")
def remove_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("sessions.assign")),
):
    """Remove a session assignment (requires sessions.assign permission)"""
    success = SessionService(db).remove_assignment(assignment_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    return {"message": "Assignment removed successfully"}
