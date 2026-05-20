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

    return {"items": [_to_response(item) for item in items], "total": total}


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
    _validate_quarterly_report_input(report_data, client)

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

    report_id: int | None = None

    try:
        db.add(report)
        db.commit()
        db.refresh(report)
        report_id = report.id

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
        if report_id is not None:
            _mark_report_failed(db, report_id)
        raise

    return _to_response(report)


def get_report_pdf_path(db: Session, report_id: int) -> str | None:
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report or not report.file_path:
        return None

    file_path = Path(report.file_path).resolve()
    output_dir = settings.report_output_dir.resolve()

    if not file_path.is_relative_to(output_dir):
        return None

    return str(file_path) if file_path.is_file() else None


def _mark_report_failed(db: Session, report_id: int) -> None:
    try:
        failed_report = db.query(Report).filter(Report.id == report_id).first()

        if failed_report:
            failed_report.status = "failed"
            db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


def _ensure_client_exists(db: Session, client_id: int) -> Client:
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise ValueError("Client not found")

    return client


def _validate_quarterly_report_input(report_data: QuarterlyReportGenerateRequest, client: Client) -> None:
    client_is_married = client.marital_status == "married"

    if report_data.is_married != client_is_married:
        raise ValueError("Report household status does not match client marital status")

    if not report_data.tcc.client_1_retirement_balances:
        raise ValueError("Missing required quarterly balance: Client 1 retirement balances")

    if not report_data.tcc.non_retirement_balances:
        raise ValueError("Missing required quarterly balance: Non-retirement balances")

    _ensure_valid_numeric_map(report_data.tcc.client_1_retirement_balances, "Client 1 retirement")
    _ensure_valid_numeric_map(report_data.tcc.non_retirement_balances, "Non-retirement")
    _ensure_valid_numeric_map(report_data.tcc.liability_balances, "Liabilities")

    if report_data.is_married:
        if report_data.sacs.client_2_quarterly_inflow is None:
            raise ValueError("Missing required field: client_2_quarterly_inflow")

        if report_data.sacs.client_2_quarterly_expense is None:
            raise ValueError("Missing required field: client_2_quarterly_expense")

        if not report_data.tcc.client_2_retirement_balances:
            raise ValueError("Missing required quarterly balance: Client 2 retirement balances")

        _ensure_valid_numeric_map(report_data.tcc.client_2_retirement_balances, "Client 2 retirement")
    else:
        if report_data.sacs.client_2_quarterly_inflow is not None:
            raise ValueError("Client 2 report data is only allowed for married clients")

        if report_data.sacs.client_2_quarterly_expense is not None:
            raise ValueError("Client 2 report data is only allowed for married clients")

        if report_data.tcc.client_2_retirement_balances:
            raise ValueError("Client 2 report data is only allowed for married clients")


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
