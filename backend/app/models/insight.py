"""AI-generated board commentary."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, uuid_pk
from app.models.source import ReportingPeriod


class Insight(Base):
    """Commentary produced by the insight service.

    The insight service is given computed metrics only and never raw document
    text, per the separation principle. prompt_version and fixture_path record
    which prompt and which cached output produced this commentary.
    """

    __tablename__ = "insight"
    __table_args__ = (
        UniqueConstraint("reporting_period_id", "section", "prompt_version", name="uq_insight"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    reporting_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reporting_period.id"), nullable=False
    )
    section: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(32), nullable=False)
    fixture_path: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    reporting_period: Mapped[ReportingPeriod] = relationship()
