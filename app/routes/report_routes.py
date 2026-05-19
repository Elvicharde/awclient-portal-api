from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import report_controller
from app.schemas.report_schema import ReportResponse


router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("", response_model=list[ReportResponse])
def get_reports(db: Session = Depends(get_db)) -> list[ReportResponse]:
    return report_controller.list_reports(db)
