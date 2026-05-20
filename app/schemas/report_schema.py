from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ReportStatus = Literal["pending", "generated", "failed"]
Quarter = Literal["Q1", "Q2", "Q3", "Q4"]


class SacsInput(BaseModel):
    client_1_quarterly_inflow: float = Field(..., ge=0)
    client_1_quarterly_outflow: float = Field(..., ge=0)
    client_2_quarterly_inflow: float | None = Field(default=None, ge=0)
    client_2_quarterly_outflow: float | None = Field(default=None, ge=0)
    insurance_deductible_total: float = Field(..., ge=0)
    private_reserve_balance: float = Field(..., ge=0)
    private_reserve_target: float | None = Field(default=None, ge=0)
    excess: float | None = None


class TccInput(BaseModel):
    client_1_retirement_balances: dict[str, float] = Field(default_factory=dict)
    client_2_retirement_balances: dict[str, float] = Field(default_factory=dict)
    non_retirement_balances: dict[str, float] = Field(default_factory=dict)
    trust_property_value: float = Field(..., ge=0)
    liabilities: dict[str, float] = Field(default_factory=dict)


class QuarterlyReportGenerateRequest(BaseModel):
    client_id: int = Field(..., gt=0)
    quarter: Quarter
    is_married: bool = False
    spouse_name: str | None = Field(default=None, max_length=200)
    sacs: SacsInput
    tcc: TccInput


class SacsCalculatedTotals(BaseModel):
    total_inflow: float
    total_outflow: float
    excess: float
    insurance_deductible_total: float
    private_reserve_balance: float
    private_reserve_target: float
    monthly_expenses: float


class TccCalculatedTotals(BaseModel):
    client_1_retirement_total: float
    client_2_retirement_total: float
    non_retirement_total: float
    trust_total: float
    grand_total_net_worth: float
    liabilities_total: float


class ReportCalculatedTotals(BaseModel):
    sacs: SacsCalculatedTotals
    tcc: TccCalculatedTotals


class ReportBase(BaseModel):
    client_id: int = Field(..., gt=0)
    report_type: str = Field(default="combined", min_length=1, max_length=50)
    quarter: str | None = Field(default=None, max_length=20)
    status: ReportStatus = Field(default="pending")
    file_path: str | None = Field(default=None, max_length=500)


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    client_id: int | None = Field(default=None, gt=0)
    report_type: str | None = Field(default=None, min_length=1, max_length=50)
    quarter: str | None = Field(default=None, max_length=20)
    status: ReportStatus | None = None
    file_path: str | None = Field(default=None, max_length=500)


class ReportResponse(ReportBase):
    id: int
    input_snapshot_json: dict | None = None
    calculated_totals_json: dict | None = None
    generated_at: datetime
    pdf_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    items: list[ReportResponse]
    page: int
    limit: int
    total: int
