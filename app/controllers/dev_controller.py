from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.utils.seed import seed_demo_data


def seed_data(db: Session) -> dict[str, Any]:
    try:
        return seed_demo_data(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to seed demo data",
        ) from exc
