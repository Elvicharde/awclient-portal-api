from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.client_model import Client
from app.models.report_model import Report
from app.schemas.report_schema import ReportCreate


def get_reports(
    db: Session,
    page: int = 1,
    limit: int = 20,
    client_id: int | None = None,
    report_type: str | None = None,
) -> dict[str, Any]:
    query = db.query(Report)

    if client_id is not None:
        query = query.filter(Report.client_id == client_id)

    if report_type:
        query = query.filter(Report.report_type == report_type)

    total = query.count()
    items = (
        query.order_by(Report.generated_at.desc())
        .offset(_get_offset(page, limit))
        .limit(limit)
        .all()
    )

    return {"items": items, "page": page, "limit": limit, "total": total}


def create_report(db: Session, report_data: ReportCreate) -> Report:
    _ensure_client_exists(db, report_data.client_id)
    report = Report(**report_data.model_dump())

    try:
        db.add(report)
        db.commit()
        db.refresh(report)
    except SQLAlchemyError:
        db.rollback()
        raise

    return report


def _ensure_client_exists(db: Session, client_id: int) -> None:
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise ValueError("Client does not exist")


def _get_offset(page: int, limit: int) -> int:
    return (page - 1) * limit
