from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from io import BytesIO
from app.core.database import get_db
from app.services.export_service import ExportService
from fastapi.responses import StreamingResponse
from app.api.deps import get_current_user_id

router = APIRouter()


@router.get("/products/excel")
async def export_products_excel(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Export products to Excel format"""
    export_service = ExportService(db)
    
    excel_file = export_service.export_products_to_excel()
    
    return StreamingResponse(
        BytesIO(excel_file.getvalue()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=products.xlsx"}
    )


@router.get("/products/csv")
async def export_products_csv(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Export products to CSV format"""
    export_service = ExportService(db)
    
    csv_file = export_service.export_products_to_csv()
    
    return StreamingResponse(
        BytesIO(csv_file.getvalue()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=products.csv"}
    )


@router.get("/sessions/{session_id}/counts/excel")
async def export_session_counts_excel(
    session_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Export session counts to Excel format"""
    export_service = ExportService(db)
    
    excel_file = export_service.export_counts_to_excel(session_id)
    
    return StreamingResponse(
        BytesIO(excel_file.getvalue()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=session_{session_id}_counts.xlsx"}
    )


@router.get("/sessions/{session_id}/summary/excel")
async def export_session_summary_excel(
    session_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Export session summary to Excel format"""
    export_service = ExportService(db)
    
    excel_file = export_service.export_session_summary_to_excel(session_id)
    
    return StreamingResponse(
        BytesIO(excel_file.getvalue()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=session_{session_id}_summary.xlsx"}
    )


@router.get("/sessions/{session_id}/sage-evolution")
async def export_sage_evolution_format(
    session_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Export session in Sage Evolution compatible format"""
    export_service = ExportService(db)
    
    excel_file = export_service.export_sage_evolution_format(session_id)
    
    return StreamingResponse(
        BytesIO(excel_file.getvalue()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=sage_evolution_stockcount.xlsx"}
    )
