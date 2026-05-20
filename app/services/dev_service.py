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


def _demo_clients() -> list[dict[str, str]]:
    return [
        {
            "first_name": "Morgan",
            "last_name": "Single",
            "email": "morgan.single@example.com",
            "phone": "555-0101",
        },
        {
            "first_name": "Avery",
            "last_name": "Married",
            "email": "avery.married@example.com",
            "phone": "555-0102",
        },
    ]
