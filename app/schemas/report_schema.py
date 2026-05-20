from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


ReportStatus = Literal["pending", "generated", "failed"]
Quarter = Literal["Q1", "Q2", "Q3", "Q4"]


class SacsInput(BaseModel):
    client_1_quarterly_inflow: float = Field(..., ge=0, description="Client 1 quarterly inflow")
    client_1_quarterly_expense: float = Field(
        ...,
        ge=0,
        description="Client 1 quarterly expense/outflow",
        validation_alias=AliasChoices("client_1_quarterly_expense", "client_1_quarterly_outflow"),
    )
    client_2_quarterly_inflow: float | None = Field(default=None, ge=0, description="Client 2 quarterly inflow, married only")
    client_2_quarterly_expense: float | None = Field(
        default=None,
        ge=0,
        description="Client 2 quarterly expense/outflow, married only",
        validation_alias=AliasChoices("client_2_quarterly_expense", "client_2_quarterly_outflow"),
    )
    insurance_deductible_total: float = Field(..., ge=0, description="Household insurance deductible total")
    private_reserve_balance: float = Field(..., ge=0, description="Current private reserve balance")
    private_reserve_target: float | None = Field(default=None, ge=0, description="Client-supplied private reserve target, recalculated server-side")
    excess: float | None = Field(default=None, description="Client-supplied excess, recalculated server-side")

    model_config = ConfigDict(populate_by_name=True)


class TccInput(BaseModel):
    client_1_retirement_balances: dict[str, float] = Field(default_factory=dict, description="Client 1 retirement balances")
    client_2_retirement_balances: dict[str, float] = Field(default_factory=dict, description="Client 2 retirement balances, married only")
    non_retirement_balances: dict[str, float] = Field(default_factory=dict, description="Non-retirement balances, excluding trust/property")
    trust_value: float = Field(
        ...,
        ge=0,
        description="Trust/property value. Excluded from non-retirement total.",
        validation_alias=AliasChoices("trust_value", "trust_property_value"),
    )
    liability_balances: dict[str, float] = Field(
        default_factory=dict,
        description="Liability balances. Displayed separately and not subtracted from net worth.",
        validation_alias=AliasChoices("liability_balances", "liabilities"),
    )

    model_config = ConfigDict(populate_by_name=True)


class QuarterlyReportGenerateRequest(BaseModel):
    client_id: int = Field(..., gt=0, description="Client ID")
    quarter: Quarter = Field(..., description="Quarter being reported")
    is_married: bool = Field(default=False, description="Whether the selected client household is married")
    spouse_name: str | None = Field(default=None, max_length=200, description="Spouse display name for married households")
    sacs: SacsInput = Field(..., description="SACS cashflow data")
    tcc: TccInput = Field(..., description="TCC balance data")


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
    total: int
