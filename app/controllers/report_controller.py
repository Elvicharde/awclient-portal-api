from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas.report_schema import QuarterlyReportGenerateRequest, ReportCreate
from app.services import report_service


def list_reports(
    db: Session,
    page: int,
    limit: int,
    client_id: int | None,
    report_type: str | None,
) -> dict[str, Any]:
    try:
        return report_service.get_reports(
            db,
            page=page,
            limit=limit,
            client_id=client_id,
            report_type=report_type,
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve reports",
        ) from exc


def get_report(report_id: int, db: Session) -> dict[str, Any]:
    try:
        report = report_service.get_report_by_id(db, report_id)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve report",
        ) from exc

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    return report


def create_report(report_data: ReportCreate, db: Session) -> Any:
    try:
        return report_service.create_report(db, report_data)
    except ValueError as exc:
        status_code = status.HTTP_404_NOT_FOUND if str(exc) == "Client not found" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create report",
        ) from exc


def generate_report(report_data: QuarterlyReportGenerateRequest, db: Session) -> dict[str, Any]:
    try:
        return report_service.generate_quarterly_report(db, report_data)
    except ValueError as exc:
        status_code = status.HTTP_404_NOT_FOUND if str(exc) == "Client not found" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to persist report",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate report PDF",
        ) from exc


def get_report_pdf_path(report_id: int, db: Session) -> str:
    try:
        file_path = report_service.get_report_pdf_path(db, report_id)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve report PDF",
        ) from exc

    if not file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report PDF not found")

    return file_path
