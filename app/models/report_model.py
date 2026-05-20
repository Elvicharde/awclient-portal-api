from datetime import datetime

from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    quarter: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    input_snapshot_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    calculated_totals_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    client = relationship("Client", back_populates="reports")
