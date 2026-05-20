from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import log_controller
from app.schemas.log_schema import LogCreate, LogListResponse, LogResponse, LogUpdate


router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=LogListResponse)
def get_logs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    client_id: int | None = Query(default=None, ge=1),
    month: str | None = Query(default=None, min_length=7),
    db: Session = Depends(get_db),
) -> LogListResponse:
    return log_controller.list_logs(
        db,
        page=page,
        limit=limit,
        client_id=client_id,
        month=month,
    )


@router.get("/{log_id}", response_model=LogResponse)
def get_log(log_id: int, db: Session = Depends(get_db)) -> LogResponse:
    return log_controller.get_log(log_id, db)


@router.post("", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
def create_log(log_data: LogCreate, db: Session = Depends(get_db)) -> LogResponse:
    return log_controller.create_log(log_data, db)


@router.put("/{log_id}", response_model=LogResponse)
def update_log(
    log_id: int,
    log_data: LogUpdate,
    db: Session = Depends(get_db),
) -> LogResponse:
    return log_controller.update_log(log_id, log_data, db)
