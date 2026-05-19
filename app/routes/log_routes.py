from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import log_controller
from app.schemas.log_schema import LogCreate, LogResponse, LogUpdate


router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=list[LogResponse])
def get_logs(db: Session = Depends(get_db)) -> list[LogResponse]:
    return log_controller.list_logs(db)


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
