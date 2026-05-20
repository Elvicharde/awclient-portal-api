from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class LogBase(BaseModel):
    client_id: int = Field(..., gt=0, description="Associated client ID")
    month: str = Field(..., min_length=7, max_length=20, description="Log month, for example 2025-08")
    assets: Decimal = Field(default=Decimal("0"), ge=0, description="Assets total")
    liabilities: Decimal = Field(default=Decimal("0"), ge=0, description="Liabilities total")
    contributions: Decimal = Field(default=Decimal("0"), ge=0, description="Contributions total")
    notes: str | None = Field(default=None, max_length=2000)


class LogCreate(LogBase):
    pass


class LogUpdate(BaseModel):
    client_id: int | None = Field(default=None, gt=0)
    month: str | None = Field(default=None, min_length=7, max_length=20)
    assets: Decimal | None = Field(default=None, ge=0)
    liabilities: Decimal | None = Field(default=None, ge=0)
    contributions: Decimal | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=2000)


class LogResponse(LogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LogListResponse(BaseModel):
    items: list[LogResponse]
    page: int
    limit: int
    total: int
