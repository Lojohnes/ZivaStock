from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.services.report_service import ReportService
from app.models.user import User
from app.api.deps import get_current_user_id, require_permission

router = APIRouter()


@router.get("/variance")
def generate_variance_report(
    session_id: int = Query(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Generate variance report for a session"""
    report_service = ReportService(db)
    try:
        return report_service.generate_variance_report(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/session-progress")
def get_session_progress(
    session_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get session progress summary (v_session_progress)"""
    report_service = ReportService(db)
    return report_service.get_session_progress(session_id)


@router.get("/duplicates")
def generate_duplicate_report(
    session_id: int = Query(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Generate duplicate count report from synchronized server counts."""
    try:
        return ReportService(db).generate_duplicate_report(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/missing")
def generate_missing_stock_report(
    session_id: int = Query(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Generate missing stock report"""
    report_service = ReportService(db)
    try:
        return report_service.generate_missing_stock_report(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/productivity")
def generate_user_productivity_report(
    session_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Generate user productivity report"""
    report_service = ReportService(db)
    return report_service.generate_user_productivity_report(session_id)


@router.get("/audit")
def generate_audit_report(
    user_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("reports.view_audit")),
):
    """Generate audit trail report (requires reports.view_audit permission)"""
    report_service = ReportService(db)
    return report_service.generate_audit_report(user_id, start_date, end_date)


@router.get("/historical")
def generate_historical_report(
    month: str = Query(...),
    location_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Generate historical stocktake report"""
    # Parse month (format: YYYY-MM)
    try:
        year, month_num = map(int, month.split('-'))
        start_date = datetime(year, month_num, 1)
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month_num + 1, 1)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid month format. Use YYYY-MM")
    
    from app.models.session import StocktakeSession
    query = db.query(StocktakeSession).filter(
        StocktakeSession.created_at >= start_date,
        StocktakeSession.created_at < end_date
    )
    
    if location_id:
        query = query.filter(StocktakeSession.location_id == location_id)
    
    sessions = query.all()
    
    return {
        "month": month,
        "location_id": location_id,
        "sessions": [
            {
                "id": s.id,
                "name": s.name,
                "status": s.status,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "created_at": s.created_at.isoformat()
            }
            for s in sessions
        ]
    }


@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get dashboard analytics summary"""
    report_service = ReportService(db)
    return report_service.get_dashboard_stats()
