from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas.report_schema import ReportCreate
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


def create_report(report_data: ReportCreate, db: Session) -> Any:
    try:
        return report_service.create_report(db, report_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create report",
        ) from exc
