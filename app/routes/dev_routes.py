from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import dev_controller


router = APIRouter(prefix="/api/dev", tags=["dev"])


@router.post("/seed")
def seed_demo_data(db: Session = Depends(get_db)) -> dict[str, Any]:
    return dev_controller.seed_data(db)


# Local/dev only. Do not use this endpoint for production data management.
@router.post("/reset-seed")
def reset_seed_demo_data(db: Session = Depends(get_db)) -> dict[str, Any]:
    return dev_controller.reset_seed_data(db)
