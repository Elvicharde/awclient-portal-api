from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas.log_schema import LogCreate, LogUpdate
from app.services import log_service


def list_logs(db: Session) -> list[Any]:
    try:
        return log_service.get_logs(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve logs",
        ) from exc


def create_log(log_data: LogCreate, db: Session) -> Any:
    try:
        return log_service.create_log(db, log_data)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create log",
        ) from exc


def update_log(log_id: int, log_data: LogUpdate, db: Session) -> Any:
    try:
        monthly_log = log_service.update_log(db, log_id, log_data)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to update log",
        ) from exc

    if not monthly_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found",
        )

    return monthly_log
