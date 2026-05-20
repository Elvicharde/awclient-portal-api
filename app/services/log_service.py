from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.client_model import Client
from app.models.log_model import MonthlyLog
from app.schemas.log_schema import LogCreate, LogUpdate


def get_logs(
    db: Session,
    page: int = 1,
    limit: int = 20,
    client_id: int | None = None,
    month: str | None = None,
) -> dict[str, Any]:
    query = db.query(MonthlyLog)

    if client_id is not None:
        query = query.filter(MonthlyLog.client_id == client_id)

    if month:
        query = query.filter(MonthlyLog.month == month)

    total = query.count()
    items = (
        query.order_by(MonthlyLog.created_at.desc())
        .offset(_get_offset(page, limit))
        .limit(limit)
        .all()
    )

    return {"items": items, "page": page, "limit": limit, "total": total}


def get_log_by_id(db: Session, log_id: int) -> MonthlyLog | None:
    return db.query(MonthlyLog).filter(MonthlyLog.id == log_id).first()


def create_log(db: Session, log_data: LogCreate) -> MonthlyLog:
    _ensure_client_exists(db, log_data.client_id)
    _ensure_month_is_present(log_data.month)
    monthly_log = MonthlyLog(**log_data.model_dump())

    try:
        db.add(monthly_log)
        db.commit()
        db.refresh(monthly_log)
    except SQLAlchemyError:
        db.rollback()
        raise

    return monthly_log


def update_log(db: Session, log_id: int, log_data: LogUpdate) -> MonthlyLog | None:
    monthly_log = get_log_by_id(db, log_id)

    if not monthly_log:
        return None

    update_data = log_data.model_dump(exclude_unset=True)

    if "client_id" in update_data and update_data["client_id"] is not None:
        _ensure_client_exists(db, update_data["client_id"])

    if "month" in update_data and update_data["month"] is not None:
        _ensure_month_is_present(update_data["month"])

    for field, value in update_data.items():
        setattr(monthly_log, field, value)

    try:
        db.commit()
        db.refresh(monthly_log)
    except SQLAlchemyError:
        db.rollback()
        raise

    return monthly_log


def _ensure_client_exists(db: Session, client_id: int) -> None:
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise ValueError("Client does not exist")


def _ensure_month_is_present(month: str) -> None:
    if not month.strip():
        raise ValueError("Month is required")


def _get_offset(page: int, limit: int) -> int:
    return (page - 1) * limit
