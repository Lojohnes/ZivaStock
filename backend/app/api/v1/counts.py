from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.schemas.count import (
    FirstCountCreate, SecondCountCreate, CountUpdate,
    FirstCountResponse, SecondCountResponse,
    FirstCountWithDetails, SecondCountWithDetails,
)
from app.schemas.common import PaginatedResponse
from app.services.count_service import CountService
from app.models.user import User
from app.api.deps import get_current_user_id, get_current_user, require_permission

router = APIRouter()


# -------------------------------------------------------------------
# First Counts
# -------------------------------------------------------------------

@router.post("/first", response_model=FirstCountResponse, status_code=status.HTTP_201_CREATED)
def create_first_count(
    count_data: FirstCountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("counts.create")),
):
    """Submit a first count (requires counts.create permission)"""
    count_service = CountService(db)
    try:
        return count_service.create_first_count(count_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/first/bulk", response_model=List[FirstCountResponse], status_code=status.HTTP_201_CREATED)
def create_first_counts_bulk(
    counts_data: List[FirstCountCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("counts.create")),
):
    """Submit multiple first counts (requires counts.create permission)"""
    count_service = CountService(db)
    try:
        return [count_service.create_first_count(item, current_user.id) for item in counts_data]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/first", response_model=PaginatedResponse[FirstCountResponse])
def get_first_counts(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    session_id: Optional[int] = None,
    shelf_section_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get first counts with pagination and filters"""
    count_service = CountService(db)
    skip = (page - 1) * limit
    counts, total = count_service.get_first_counts(skip=skip, limit=limit, session_id=session_id, shelf_section_id=shelf_section_id, user_id=user_id)
    pages = (total + limit - 1) // limit
    return PaginatedResponse(items=counts, total=total, page=page, limit=limit, pages=pages)


@router.get("/first/{count_id}", response_model=FirstCountWithDetails)
def get_first_count(count_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """Get first count by ID with details"""
    count = CountService(db).get_first_count(count_id)
    if not count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="First count not found")
    return count


@router.put("/first/{count_id}", response_model=FirstCountResponse)
def update_first_count(
    count_id: int,
    count_data: CountUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("counts.update")),
):
    """Update a first count (requires counts.update permission)"""
    count = CountService(db).update_first_count(count_id, count_data)
    if not count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="First count not found")
    return count


@router.delete("/first/{count_id}")
def delete_first_count(
    count_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("counts.delete")),
):
    """Delete a first count (requires counts.delete permission)"""
    success = CountService(db).delete_first_count(count_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="First count not found")
    return {"message": "First count deleted successfully"}


# -------------------------------------------------------------------
# Second Counts
# -------------------------------------------------------------------

@router.post("/second", response_model=SecondCountResponse, status_code=status.HTTP_201_CREATED)
def create_second_count(
    count_data: SecondCountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("counts.create")),
):
    """Submit a second (verification) count (requires counts.create permission).
    Rejected if you are the same user who submitted the linked first count."""
    count_service = CountService(db)
    try:
        return count_service.create_second_count(count_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/second/bulk", response_model=List[SecondCountResponse], status_code=status.HTTP_201_CREATED)
def create_second_counts_bulk(
    counts_data: List[SecondCountCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("counts.create")),
):
    """Submit multiple second counts (requires counts.create permission)."""
    count_service = CountService(db)
    try:
        return [count_service.create_second_count(item, current_user.id) for item in counts_data]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/second", response_model=PaginatedResponse[SecondCountResponse])
def get_second_counts(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    session_id: Optional[int] = None,
    shelf_section_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get second counts with pagination and filters"""
    count_service = CountService(db)
    skip = (page - 1) * limit
    counts, total = count_service.get_second_counts(skip=skip, limit=limit, session_id=session_id, shelf_section_id=shelf_section_id, user_id=user_id)
    pages = (total + limit - 1) // limit
    return PaginatedResponse(items=counts, total=total, page=page, limit=limit, pages=pages)


@router.get("/second/{count_id}", response_model=SecondCountWithDetails)
def get_second_count(count_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """Get second count by ID with details"""
    count = CountService(db).get_second_count(count_id)
    if not count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Second count not found")
    return count


@router.put("/second/{count_id}", response_model=SecondCountResponse)
def update_second_count(
    count_id: int,
    count_data: CountUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("counts.update")),
):
    """Update a second count (requires counts.update permission)"""
    count = CountService(db).update_second_count(count_id, count_data)
    if not count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Second count not found")
    return count


@router.delete("/second/{count_id}")
def delete_second_count(
    count_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("counts.delete")),
):
    """Delete a second count (requires counts.delete permission)"""
    success = CountService(db).delete_second_count(count_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Second count not found")
    return {"message": "Second count deleted successfully"}
