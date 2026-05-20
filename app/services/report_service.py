from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.client_model import Client
from app.models.report_model import Report
from app.schemas.report_schema import QuarterlyReportGenerateRequest, ReportCreate
from app.services import calculation_service, pdf_service


def get_reports(
    db: Session,
    page: int = 1,
    limit: int = 20,
    client_id: int | None = None,
    report_type: str | None = None,
) -> dict[str, Any]:
    query = db.query(Report)

    if client_id is not None:
        query = query.filter(Report.client_id == client_id)

    if report_type:
        query = query.filter(Report.report_type == report_type)

    total = query.count()
    items = (
        query.order_by(Report.generated_at.desc())
        .offset(_get_offset(page, limit))
        .limit(limit)
        .all()
    )

    return {"items": [_to_response(item) for item in items], "page": page, "limit": limit, "total": total}


def get_report_by_id(db: Session, report_id: int) -> dict[str, Any] | None:
    report = db.query(Report).filter(Report.id == report_id).first()

    return _to_response(report) if report else None


def create_report(db: Session, report_data: ReportCreate) -> Report:
    _ensure_client_exists(db, report_data.client_id)
    report = Report(**report_data.model_dump())

    try:
        db.add(report)
        db.commit()
        db.refresh(report)
    except SQLAlchemyError:
        db.rollback()
        raise

    return report


def generate_quarterly_report(
    db: Session,
    report_data: QuarterlyReportGenerateRequest,
) -> dict[str, Any]:
    client = _ensure_client_exists(db, report_data.client_id)
    _validate_quarterly_report_input(report_data)

    sacs_totals = calculation_service.calculate_sacs_totals(report_data.sacs, report_data.is_married)
    tcc_totals = calculation_service.calculate_tcc_totals(report_data.tcc, report_data.is_married)
    calculated_totals = {"sacs": sacs_totals, "tcc": tcc_totals}
    input_snapshot = report_data.model_dump()

    report = Report(
        client_id=report_data.client_id,
        quarter=report_data.quarter,
        report_type="combined",
        status="pending",
        input_snapshot_json=input_snapshot,
        calculated_totals_json=calculated_totals,
    )

    try:
        db.add(report)
        db.commit()
        db.refresh(report)

        pdf_path = pdf_service.generate_combined_report_pdf(
            report.id,
            _build_pdf_context(client, report_data, calculated_totals),
        )
        report.file_path = pdf_path
        report.status = "generated"
        db.commit()
        db.refresh(report)
    except Exception:
        db.rollback()
        if "report" in locals() and report.id:
            report.status = "failed"
            db.add(report)
            db.commit()
        raise

    return _to_response(report)


def get_report_pdf_path(db: Session, report_id: int) -> str | None:
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report or not report.file_path:
        return None

    file_path = Path(report.file_path).resolve()
    output_dir = settings.report_output_dir.resolve()

    if output_dir not in file_path.parents:
        return None

    return str(file_path) if file_path.is_file() else None


def _ensure_client_exists(db: Session, client_id: int) -> Client:
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise ValueError("Client not found")

    return client


def _validate_quarterly_report_input(report_data: QuarterlyReportGenerateRequest) -> None:
    if not report_data.tcc.client_1_retirement_balances:
        raise ValueError("Missing required quarterly balance: Client 1 retirement balances")

    if not report_data.tcc.non_retirement_balances:
        raise ValueError("Missing required quarterly balance: Non-retirement balances")

    _ensure_valid_numeric_map(report_data.tcc.client_1_retirement_balances, "Client 1 retirement")
    _ensure_valid_numeric_map(report_data.tcc.non_retirement_balances, "Non-retirement")
    _ensure_valid_numeric_map(report_data.tcc.liabilities, "Liabilities")

    if report_data.is_married:
        if report_data.sacs.client_2_quarterly_inflow is None:
            raise ValueError("Missing required SACS field: Client 2 quarterly inflow")

        if report_data.sacs.client_2_quarterly_outflow is None:
            raise ValueError("Missing required SACS field: Client 2 quarterly outflow")

        if not report_data.tcc.client_2_retirement_balances:
            raise ValueError("Missing required quarterly balance: Client 2 retirement balances")

        _ensure_valid_numeric_map(report_data.tcc.client_2_retirement_balances, "Client 2 retirement")


def _ensure_valid_numeric_map(values: dict[str, float], label: str) -> None:
    for key, value in values.items():
        if key.strip() == "":
            raise ValueError(f"{label} contains an unnamed value")

        if value < 0:
            raise ValueError(f"{label} value cannot be negative")


def _build_pdf_context(
    client: Client,
    report_data: QuarterlyReportGenerateRequest,
    calculated_totals: dict[str, Any],
) -> dict[str, Any]:
    return {
        "client_name": f"{client.first_name} {client.last_name}",
        "spouse_name": report_data.spouse_name if report_data.is_married else None,
        "quarter": report_data.quarter,
        "generated_at": datetime.utcnow().strftime("%B %d, %Y"),
        "inputs": report_data.model_dump(),
        "totals": calculated_totals,
    }


def _to_response(report: Report) -> dict[str, Any]:
    return {
        "id": report.id,
        "client_id": report.client_id,
        "report_type": report.report_type,
        "quarter": report.quarter,
        "status": report.status,
        "file_path": report.file_path,
        "input_snapshot_json": report.input_snapshot_json,
        "calculated_totals_json": report.calculated_totals_json,
        "generated_at": report.generated_at,
        "pdf_url": f"/api/reports/{report.id}/pdf" if report.file_path else None,
    }


def _get_offset(page: int, limit: int) -> int:
    return (page - 1) * limit
