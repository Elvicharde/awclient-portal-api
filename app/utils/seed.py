from datetime import date
from typing import Any

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.client_model import Client
from app.models.log_model import MonthlyLog
from app.models.report_model import Report


def reset_demo_data(db: Session) -> dict[str, int | str]:
    """Local/dev only: remove demo records and reseed a clean demo dataset."""
    try:
        deleted_reports = db.query(Report).delete()
        deleted_logs = db.query(MonthlyLog).delete()
        deleted_clients = db.query(Client).delete()
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    seed_result = seed_demo_data(db)

    return {
        "status": "reset_seeded",
        "deleted_reports": deleted_reports,
        "deleted_logs": deleted_logs,
        "deleted_clients": deleted_clients,
        "created_clients": seed_result["created_clients"],
    }


def seed_demo_data(db: Session) -> dict[str, Any]:
    created_clients: list[Client] = []

    try:
        for client_data in _demo_clients():
            existing_client = (
                db.query(Client)
                .filter(func.lower(Client.email) == client_data["email"].lower())
                .first()
            )

            if existing_client:
                continue

            client = Client(**client_data)
            db.add(client)
            created_clients.append(client)

        db.commit()

        for client in created_clients:
            db.refresh(client)
    except SQLAlchemyError:
        db.rollback()
        raise

    return {
        "status": "seeded",
        "created_clients": len(created_clients),
        "clients": [
            {
                "id": client.id,
                "name": f"{client.first_name} {client.last_name}",
                "marital_status": client.marital_status,
                "email": client.email,
            }
            for client in created_clients
        ],
    }


def _demo_clients() -> list[dict[str, Any]]:
    return [
        {
            "first_name": "Morgan",
            "middle_name": "A",
            "last_name": "Single",
            "date_of_birth": date(1984, 6, 14),
            "ssn_last_four": "1234",
            "email": "morgan.single@example.com",
            "phone": "555-0101",
            "marital_status": "single",
            "client_1_monthly_salary_after_tax": 15000,
            "client_1_monthly_expense_budget": 9000,
            "private_reserve_target": 56000,
            "insurance_deductible_total": 2000,
            "retirement_accounts_json": {
                "IRA": True,
                "401K": True,
            },
            "non_retirement_accounts_json": {
                "Brokerage": True,
                "Checking": True,
            },
            "trust_details_json": {
                "has_trust": False,
                "trust_name": None,
                "property_address": None,
                "city": None,
                "state": None,
                "zip": None,
            },
            "liabilities_json": {
                "Mortgage": 308000,
                "Credit card": 6200,
            },
        },
        {
            "first_name": "Avery",
            "middle_name": "B",
            "last_name": "Married",
            "date_of_birth": date(1979, 3, 22),
            "ssn_last_four": "5678",
            "email": "avery.married@example.com",
            "phone": "555-0102",
            "marital_status": "married",
            "spouse_first_name": "Jordan",
            "spouse_middle_name": "C",
            "spouse_last_name": "Married",
            "spouse_date_of_birth": date(1981, 9, 10),
            "spouse_ssn_last_four": "2468",
            "spouse_email": "jordan.married@example.com",
            "spouse_phone": "555-0103",
            "client_1_monthly_salary_after_tax": 15000,
            "client_1_monthly_expense_budget": 9000,
            "client_2_monthly_salary_after_tax": 8000,
            "client_2_monthly_expense_budget": 5000,
            "private_reserve_target": 87000,
            "insurance_deductible_total": 3000,
            "retirement_accounts_json": {
                "client_1": ["IRA", "401K"],
                "client_2": ["Roth IRA", "Pension"],
            },
            "non_retirement_accounts_json": {
                "Joint Brokerage": True,
                "Checking": True,
                "Savings": True,
            },
            "trust_details_json": {
                "has_trust": True,
                "trust_name": "Married Family Trust",
                "property_address": "100 Main Street",
                "city": "Austin",
                "state": "TX",
                "zip": "78701",
            },
            "liabilities_json": {
                "Mortgage": 350000,
                "Auto loan": 22000,
                "Credit card": 8500,
            },
        },
    ]
