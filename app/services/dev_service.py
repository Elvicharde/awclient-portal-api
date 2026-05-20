from datetime import date
from typing import Any

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.client_model import Client
from app.models import log_model, report_model


def seed_demo_data(db: Session) -> dict[str, int | str]:
    created_count = 0

    for client_data in _demo_clients():
        existing_client = (
            db.query(Client)
            .filter(func.lower(Client.email) == client_data["email"].lower())
            .first()
        )

        if existing_client:
            continue

        db.add(Client(**client_data))
        created_count += 1

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return {
        "status": "seeded",
        "created_clients": created_count,
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
            "retirement_accounts_json": {"IRA": True, "401K": True},
            "non_retirement_accounts_json": {"Brokerage": True, "Checking": True},
            "trust_details_json": {"has_trust": False, "property_address": None},
            "liabilities_json": {"Mortgage": True, "Credit card": True},
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
            "non_retirement_accounts_json": {"Joint Brokerage": True, "Checking": True, "Savings": True},
            "trust_details_json": {"has_trust": True, "trust_name": "Married Family Trust"},
            "liabilities_json": {"Mortgage": True, "Auto loan": True, "Credit card": True},
        },
    ]
