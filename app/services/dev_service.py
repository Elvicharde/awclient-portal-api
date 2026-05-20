from typing import Any

from sqlalchemy.orm import Session

from app.utils import seed


def seed_demo_data(db: Session) -> dict[str, Any]:
    return seed.seed_demo_data(db)


def reset_seed_demo_data(db: Session) -> dict[str, Any]:
    return seed.reset_demo_data(db)
