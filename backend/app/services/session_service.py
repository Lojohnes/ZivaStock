from sqlalchemy.orm import Session
from app.models.session import StocktakeSession, SessionAssignment
from app.models.location import Location, Shelf, ShelfSection
from app.schemas.session import SessionCreate, SessionUpdate, SessionAssignmentCreate
from typing import Optional, List
from datetime import datetime

# Valid forward transitions for a stocktake session's lifecycle
_VALID_TRANSITIONS = {
    "not_started": {"in_progress", "cancelled"},
    "in_progress": {"paused", "counting_complete", "cancelled"},
    "paused": {"in_progress", "cancelled"},
    "counting_complete": {"reconciling", "in_progress"},
    "reconciling": {"completed"},
    "completed": {"archived"},
    "archived": set(),
    "cancelled": set(),
}


class SessionService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_session(self, session_id: int) -> Optional[StocktakeSession]:
        """Get session by ID"""
        return self.db.query(StocktakeSession).filter(StocktakeSession.id == session_id).first()
    
    def get_sessions(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        location_id: Optional[int] = None,
        session_type: Optional[str] = None,
    ) -> tuple[List[StocktakeSession], int]:
        """Get sessions with pagination and filters"""
        query = self.db.query(StocktakeSession)

        if status:
            query = query.filter(StocktakeSession.status == status)
        if location_id:
            query = query.filter(StocktakeSession.location_id == location_id)
        if session_type:
            query = query.filter(StocktakeSession.session_type == session_type)

        total = query.count()
        sessions = query.order_by(StocktakeSession.created_at.desc()).offset(skip).limit(limit).all()

        return sessions, total

    def get_session_sections(self, session_id: int) -> List[ShelfSection]:
        """Get shelf sections associated with a session via its location"""
        session = self.get_session(session_id)
        if not session:
            return []
        return (
            self.db.query(ShelfSection)
            .join(Shelf, ShelfSection.shelf_id == Shelf.id)
            .filter(Shelf.location_id == session.location_id)
            .order_by(ShelfSection.name)
            .all()
        )

    def create_session(self, session_data: SessionCreate, user_id: int) -> StocktakeSession:
        """Create a new stocktake session"""
        # Verify location exists
        location = self.db.query(Location).filter(Location.id == session_data.location_id).first()
        if not location:
            raise ValueError("Location not found")

        db_session = StocktakeSession(
            **session_data.model_dump(),
            created_by=user_id,
            status="not_started"
        )

        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)

        # Register the creator as a supervisor by default
        self.assign_user(db_session.id, SessionAssignmentCreate(user_id=user_id, assignment_role="supervisor"), assigned_by=user_id)

        return db_session
    
    def update_session(self, session_id: int, session_data: SessionUpdate) -> Optional[StocktakeSession]:
        """Update session"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        update_data = session_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session, field, value)
        
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def _transition(self, session_id: int, new_status: str) -> Optional[StocktakeSession]:
        session = self.get_session(session_id)
        if not session:
            return None
        allowed = _VALID_TRANSITIONS.get(session.status, set())
        if new_status not in allowed:
            raise ValueError(f"Cannot transition session from '{session.status}' to '{new_status}'")

        session.status = new_status
        if new_status == "in_progress" and session.start_time is None:
            session.start_time = datetime.utcnow()
        if new_status == "completed":
            session.end_time = datetime.utcnow()

        self.db.commit()
        self.db.refresh(session)
        return session

    def start_session(self, session_id: int) -> Optional[StocktakeSession]:
        return self._transition(session_id, "in_progress")

    def pause_session(self, session_id: int) -> Optional[StocktakeSession]:
        return self._transition(session_id, "paused")

    def resume_session(self, session_id: int) -> Optional[StocktakeSession]:
        return self._transition(session_id, "in_progress")

    def mark_counting_complete(self, session_id: int) -> Optional[StocktakeSession]:
        return self._transition(session_id, "counting_complete")

    def start_reconciling(self, session_id: int) -> Optional[StocktakeSession]:
        return self._transition(session_id, "reconciling")

    def complete_session(self, session_id: int, approved_by: int) -> Optional[StocktakeSession]:
        """Complete a session (transitions from 'reconciling' -> 'completed')"""
        session = self._transition(session_id, "completed")
        if session:
            session.approved_by = approved_by
            session.approved_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(session)
        return session

    def archive_session(self, session_id: int) -> Optional[StocktakeSession]:
        return self._transition(session_id, "archived")

    def cancel_session(self, session_id: int) -> Optional[StocktakeSession]:
        return self._transition(session_id, "cancelled")

    # -------------------------------------------------------------------
    # Session Assignments
    # -------------------------------------------------------------------

    def assign_user(
        self, session_id: int, assignment_data: SessionAssignmentCreate, assigned_by: Optional[int] = None
    ) -> Optional[SessionAssignment]:
        """Assign a user (optionally scoped to a shelf section) to a session"""
        session = self.get_session(session_id)
        if not session:
            return None

        existing = (
            self.db.query(SessionAssignment)
            .filter(
                SessionAssignment.session_id == session_id,
                SessionAssignment.user_id == assignment_data.user_id,
                SessionAssignment.shelf_section_id == assignment_data.shelf_section_id,
                SessionAssignment.assignment_role == assignment_data.assignment_role,
            )
            .first()
        )
        if existing:
            return existing

        assignment = SessionAssignment(
            session_id=session_id,
            assigned_by=assigned_by,
            **assignment_data.model_dump(),
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def get_session_assignments(self, session_id: int) -> List[SessionAssignment]:
        """Get all assignments for a session"""
        return self.db.query(SessionAssignment).filter(SessionAssignment.session_id == session_id).all()

    def remove_assignment(self, assignment_id: int) -> bool:
        assignment = self.db.query(SessionAssignment).filter(SessionAssignment.id == assignment_id).first()
        if not assignment:
            return False
        self.db.delete(assignment)
        self.db.commit()
        return True
