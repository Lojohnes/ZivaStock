from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.schemas.adjustment import AdjustmentResponse, AdjustmentRejectRequest, SessionVarianceResponse
from app.schemas.count import DiscrepancyResponse
from app.schemas.common import PaginatedResponse
from app.services.adjustment_service import AdjustmentService
from app.models.user import User
from app.api.deps import get_current_user_id, require_permission

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AdjustmentResponse])
def get_adjustments(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    session_id: Optional[int] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    adjustment_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Get adjustments with pagination and filters"""
    service = AdjustmentService(db)
    skip = (page - 1) * limit
    items, total = service.get_adjustments(skip=skip, limit=limit, session_id=session_id, status=status_filter, adjustment_type=adjustment_type)
    pages = (total + limit - 1) // limit
    return PaginatedResponse(items=items, total=total, page=page, limit=limit, pages=pages)


@router.get("/{adjustment_id}", response_model=AdjustmentResponse)
def get_adjustment(adjustment_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """Get adjustment by ID"""
    adjustment = AdjustmentService(db).get_adjustment(adjustment_id)
    if not adjustment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adjustment not found")
    return adjustment


@router.post("/sessions/{session_id}/generate", response_model=dict)
def generate_adjustments(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("adjustments.create")),
):
    """Generate/refresh adjustments for a session from first/second counts
    vs. system quantity (requires adjustments.create permission)"""
    affected = AdjustmentService(db).generate_adjustments(session_id, current_user.id)
    return {"affected_rows": affected}


@router.get("/sessions/{session_id}/variance", response_model=SessionVarianceResponse)
def get_session_variance(session_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """Get variance summary for a session's adjustments"""
    return AdjustmentService(db).get_session_variance(session_id)


@router.get("/sessions/{session_id}/discrepancies", response_model=List[DiscrepancyResponse])
def get_discrepancies(
    session_id: int,
    tolerance_pct: float = Query(0, ge=0, le=100),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Get first/second count discrepancies beyond tolerance, pre-adjustment"""
    return AdjustmentService(db).get_discrepancies(session_id, tolerance_pct)


@router.post("/{adjustment_id}/approve", response_model=AdjustmentResponse)
def approve_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("adjustments.approve")),
):
    """Approve a pending adjustment (requires adjustments.approve permission)"""
    service = AdjustmentService(db)
    try:
        adjustment = service.approve_adjustment(adjustment_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not adjustment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adjustment not found")
    return adjustment


@router.post("/{adjustment_id}/reject", response_model=AdjustmentResponse)
def reject_adjustment(
    adjustment_id: int,
    reject_data: AdjustmentRejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("adjustments.approve")),
):
    """Reject a pending adjustment (requires adjustments.approve permission)"""
    service = AdjustmentService(db)
    try:
        adjustment = service.reject_adjustment(adjustment_id, current_user.id, reject_data.reason)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not adjustment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adjustment not found")
    return adjustment


@router.post("/{adjustment_id}/post", response_model=AdjustmentResponse)
def post_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("adjustments.post")),
):
    """Post an approved adjustment, applying it to the product's system_quantity
    (requires adjustments.post permission)"""
    service = AdjustmentService(db)
    try:
        adjustment = service.post_adjustment(adjustment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not adjustment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adjustment not found")
    return adjustment
