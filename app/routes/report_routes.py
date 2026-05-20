from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import report_controller
from app.schemas.report_schema import (
    QuarterlyReportGenerateRequest,
    ReportCreate,
    ReportListResponse,
    ReportResponse,
)


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


@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    report_data: QuarterlyReportGenerateRequest,
    db: Session = Depends(get_db),
) -> ReportResponse:
    return report_controller.generate_report(report_data, db)


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)) -> ReportResponse:
    return report_controller.get_report(report_id, db)


@router.get("/{report_id}/pdf")
def get_report_pdf(report_id: int, db: Session = Depends(get_db)) -> FileResponse:
    file_path = report_controller.get_report_pdf_path(report_id, db)

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=f"combined_report_{report_id}.pdf",
    )


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(report_data: ReportCreate, db: Session = Depends(get_db)) -> ReportResponse:
    return report_controller.create_report(report_data, db)
