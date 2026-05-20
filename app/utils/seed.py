from typing import Any

from sqlalchemy.orm import Session

from app.services import dev_service


def seed_demo_data(db: Session) -> dict[str, Any]:
    return dev_service.seed_demo_data(db)
