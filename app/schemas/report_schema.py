from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ReportStatus = Literal["pending", "generated", "failed"]


class ReportBase(BaseModel):
    client_id: int = Field(..., gt=0, description="Associated client ID")
    report_type: str = Field(..., min_length=1, max_length=50, description="Report type")
    status: ReportStatus = Field(default="pending", description="Report generation status")
    file_path: str | None = Field(default=None, max_length=500, description="Report file path placeholder")


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    client_id: int | None = Field(default=None, gt=0)
    report_type: str | None = Field(default=None, min_length=1, max_length=50)
    status: ReportStatus | None = None
    file_path: str | None = Field(default=None, max_length=500)


class ReportResponse(ReportBase):
    id: int
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    items: list[ReportResponse]
    page: int
    limit: int
    total: int
