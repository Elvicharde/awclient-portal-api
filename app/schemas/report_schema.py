from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReportBase(BaseModel):
    client_id: int
    report_type: str
    file_path: str | None = None


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    client_id: int | None = None
    report_type: str | None = None
    file_path: str | None = None


class ReportResponse(ReportBase):
    id: int
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
