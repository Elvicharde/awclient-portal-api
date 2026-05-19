from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class MonthlyLog(Base):
    __tablename__ = "monthly_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    month: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    assets: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    liabilities: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    contributions: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    client = relationship("Client", back_populates="logs")
