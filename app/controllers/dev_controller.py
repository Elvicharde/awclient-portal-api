from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services import dev_service


def seed_data(db: Session) -> dict[str, Any]:
    try:
        return dev_service.seed_demo_data(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to seed demo data",
        ) from exc


def reset_seed_data(db: Session) -> dict[str, Any]:
    try:
        return dev_service.reset_seed_demo_data(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to reset seed demo data",
        ) from exc
