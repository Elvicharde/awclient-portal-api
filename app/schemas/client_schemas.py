from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


MaritalStatus = Literal["single", "married"]


class ClientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Client first name")
    middle_name: str | None = Field(default=None, max_length=100, description="Client middle name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Client last name")
    date_of_birth: date | None = Field(default=None, description="Client date of birth")
    ssn_last_four: str | None = Field(default=None, min_length=4, max_length=4, description="Last four digits of SSN")
    email: EmailStr = Field(..., description="Unique client email address")
    phone: str | None = Field(default=None, max_length=50, description="Client phone number")
    marital_status: MaritalStatus = Field(default="single", description="Client household marital status")
    spouse_first_name: str | None = Field(default=None, max_length=100, description="Spouse first name, required when married")
    spouse_middle_name: str | None = Field(default=None, max_length=100, description="Spouse middle name")
    spouse_last_name: str | None = Field(default=None, max_length=100, description="Spouse last name, required when married")
    spouse_date_of_birth: date | None = Field(default=None, description="Spouse date of birth, required when married")
    spouse_ssn_last_four: str | None = Field(default=None, min_length=4, max_length=4, description="Spouse last four digits of SSN")
    spouse_email: EmailStr | None = Field(default=None, description="Spouse email")
    spouse_phone: str | None = Field(default=None, max_length=50, description="Spouse phone number")
    client_1_monthly_salary_after_tax: float | None = Field(default=None, ge=0, description="Client 1 monthly salary after tax")
    client_1_monthly_expense_budget: float | None = Field(default=None, ge=0, description="Client 1 monthly expense budget")
    client_2_monthly_salary_after_tax: float | None = Field(default=None, ge=0, description="Client 2 monthly salary after tax, required when married")
    client_2_monthly_expense_budget: float | None = Field(default=None, ge=0, description="Client 2 monthly expense budget, required when married")
    private_reserve_target: float | None = Field(default=None, ge=0, description="Household private reserve target")
    insurance_deductible_total: float | None = Field(default=None, ge=0, description="Household insurance deductible total")
    retirement_accounts_json: dict[str, Any] | None = Field(default=None, description="Retirement account structure")
    non_retirement_accounts_json: dict[str, Any] | None = Field(default=None, description="Non-retirement account structure")
    trust_details_json: dict[str, Any] | None = Field(default=None, description="Trust and property details")
    liabilities_json: dict[str, Any] | None = Field(default=None, description="Liability structure")

    @field_validator("ssn_last_four", "spouse_ssn_last_four")
    @classmethod
    def validate_ssn_last_four(cls, value: str | None) -> str | None:
        if value is not None and not value.isdigit():
            raise ValueError("SSN last four must be 4 digits")
        return value


class ClientCreate(ClientBase):
    @model_validator(mode="after")
    def validate_household_contract(self) -> "ClientCreate":
        _validate_married_household(self)
        return self


class ClientUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    date_of_birth: date | None = None
    ssn_last_four: str | None = Field(default=None, min_length=4, max_length=4)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    marital_status: MaritalStatus | None = None
    spouse_first_name: str | None = Field(default=None, max_length=100)
    spouse_middle_name: str | None = Field(default=None, max_length=100)
    spouse_last_name: str | None = Field(default=None, max_length=100)
    spouse_date_of_birth: date | None = None
    spouse_ssn_last_four: str | None = Field(default=None, min_length=4, max_length=4)
    spouse_email: EmailStr | None = None
    spouse_phone: str | None = Field(default=None, max_length=50)
    client_1_monthly_salary_after_tax: float | None = Field(default=None, ge=0)
    client_1_monthly_expense_budget: float | None = Field(default=None, ge=0)
    client_2_monthly_salary_after_tax: float | None = Field(default=None, ge=0)
    client_2_monthly_expense_budget: float | None = Field(default=None, ge=0)
    private_reserve_target: float | None = Field(default=None, ge=0)
    insurance_deductible_total: float | None = Field(default=None, ge=0)
    retirement_accounts_json: dict[str, Any] | None = None
    non_retirement_accounts_json: dict[str, Any] | None = None
    trust_details_json: dict[str, Any] | None = None
    liabilities_json: dict[str, Any] | None = None

    @field_validator("ssn_last_four", "spouse_ssn_last_four")
    @classmethod
    def validate_ssn_last_four(cls, value: str | None) -> str | None:
        if value is not None and not value.isdigit():
            raise ValueError("SSN last four must be 4 digits")
        return value


class ClientResponse(ClientBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClientListResponse(BaseModel):
    items: list[ClientResponse]
    page: int
    limit: int
    total: int


def _validate_married_household(client: ClientBase) -> None:
    if client.marital_status != "married":
        return

    required_values = {
        "spouse_first_name": client.spouse_first_name,
        "spouse_last_name": client.spouse_last_name,
        "spouse_date_of_birth": client.spouse_date_of_birth,
        "client_2_monthly_salary_after_tax": client.client_2_monthly_salary_after_tax,
        "client_2_monthly_expense_budget": client.client_2_monthly_expense_budget,
    }

    for field_name, value in required_values.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"Missing required field: {field_name}")
