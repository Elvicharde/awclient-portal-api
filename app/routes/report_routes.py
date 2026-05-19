from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import report_controller
from app.schemas.report_schema import ReportCreate, ReportListResponse, ReportResponse


router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("", response_model=ReportListResponse)
def get_reports(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    client_id: int | None = Query(default=None, ge=1),
    report_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> ReportListResponse:
    return report_controller.list_reports(
        db,
        page=page,
        limit=limit,
        client_id=client_id,
        report_type=report_type,
    )


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(report_data: ReportCreate, db: Session = Depends(get_db)) -> ReportResponse:
    return report_controller.create_report(report_data, db)
