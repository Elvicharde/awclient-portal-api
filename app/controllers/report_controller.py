from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services import report_service


def list_reports(db: Session) -> list[Any]:
    try:
        return report_service.get_reports(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve reports",
        ) from exc
