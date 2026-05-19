from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.log_model import MonthlyLog
from app.schemas.log_schema import LogCreate, LogUpdate


def get_logs(db: Session) -> list[MonthlyLog]:
    return db.query(MonthlyLog).order_by(MonthlyLog.created_at.desc()).all()


def get_log_by_id(db: Session, log_id: int) -> MonthlyLog | None:
    return db.query(MonthlyLog).filter(MonthlyLog.id == log_id).first()


def create_log(db: Session, log_data: LogCreate) -> MonthlyLog:
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

    for field, value in update_data.items():
        setattr(monthly_log, field, value)

    try:
        db.commit()
        db.refresh(monthly_log)
    except SQLAlchemyError:
        db.rollback()
        raise

    return monthly_log
