from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class LogBase(BaseModel):
    client_id: int
    month: str
    assets: Decimal = Decimal("0")
    liabilities: Decimal = Decimal("0")
    contributions: Decimal = Decimal("0")
    notes: str | None = None


class LogCreate(LogBase):
    pass


class LogUpdate(BaseModel):
    client_id: int | None = None
    month: str | None = None
    assets: Decimal | None = None
    liabilities: Decimal | None = None
    contributions: Decimal | None = None
    notes: str | None = None


class LogResponse(LogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
