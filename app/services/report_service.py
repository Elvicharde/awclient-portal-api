from sqlalchemy.orm import Session

from app.models.report_model import Report


def get_reports(db: Session) -> list[Report]:
    return db.query(Report).order_by(Report.generated_at.desc()).all()
