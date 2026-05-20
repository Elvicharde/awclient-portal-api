from datetime import date, datetime

from typing import Any

from sqlalchemy import Date, DateTime, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    ssn_last_four: Mapped[str | None] = mapped_column(String(4), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    marital_status: Mapped[str] = mapped_column(String(20), nullable=False, default="single")
    spouse_first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    spouse_middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    spouse_last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    spouse_date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    spouse_ssn_last_four: Mapped[str | None] = mapped_column(String(4), nullable=True)
    spouse_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    spouse_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    client_1_monthly_salary_after_tax: Mapped[float | None] = mapped_column(Float, nullable=True)
    client_1_monthly_expense_budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    client_2_monthly_salary_after_tax: Mapped[float | None] = mapped_column(Float, nullable=True)
    client_2_monthly_expense_budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    private_reserve_target: Mapped[float | None] = mapped_column(Float, nullable=True)
    insurance_deductible_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    retirement_accounts_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    non_retirement_accounts_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    trust_details_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    liabilities_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    logs = relationship(
        "MonthlyLog",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    reports = relationship(
        "Report",
        back_populates="client",
        cascade="all, delete-orphan",
    )
