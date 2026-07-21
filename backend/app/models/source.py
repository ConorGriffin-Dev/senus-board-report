"""Provenance entities: documents, reporting periods, extraction runs."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, uuid_pk
from app.models.enums import (
    DOCUMENT_TYPES,
    PERIOD_TYPES,
    REPORTING_BASES,
    REPORTING_ENTITIES,
)


def _in(column: str, values: tuple[str, ...]) -> str:
    joined = ", ".join(f"'{v}'" for v in values)
    return f"{column} IN ({joined})"


class SourceDocument(Base):
    """A published document that financial data was extracted from.

    reporting_entity and reporting_basis carry inventory Finding 2: annual
    figures are ADF Farm Solutions Limited on a company basis, half-year
    figures are Senus PLC consolidated. Not strictly like for like.
    """

    __tablename__ = "source_document"
    __table_args__ = (
        CheckConstraint(_in("document_type", DOCUMENT_TYPES), name="ck_document_type"),
        CheckConstraint(_in("reporting_entity", REPORTING_ENTITIES), name="ck_doc_entity"),
        CheckConstraint(_in("reporting_basis", REPORTING_BASES), name="ck_doc_basis"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    doc_ref: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    document_type: Mapped[str] = mapped_column(String(32), nullable=False)
    publication_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    page_count: Mapped[int | None] = mapped_column(Integer)
    reporting_entity: Mapped[str] = mapped_column(String(64), nullable=False)
    reporting_basis: Mapped[str] = mapped_column(String(16), nullable=False)

    extraction_runs: Mapped[list["ExtractionRun"]] = relationship(back_populates="source_document")


class ReportingPeriod(Base):
    """A period that figures are reported for.

    First-class because the four available periods differ in length, entity,
    basis and audit status, and metric availability is scoped against it.
    is_derived marks H2 FY2025, which is computed by subtraction (A-03).
    """

    __tablename__ = "reporting_period"
    __table_args__ = (
        CheckConstraint(_in("period_type", PERIOD_TYPES), name="ck_period_type"),
        CheckConstraint(_in("reporting_entity", REPORTING_ENTITIES), name="ck_period_entity"),
        CheckConstraint(_in("reporting_basis", REPORTING_BASES), name="ck_period_basis"),
        CheckConstraint("end_date > start_date", name="ck_period_dates"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    label: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    period_type: Mapped[str] = mapped_column(String(16), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_audited: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reporting_entity: Mapped[str] = mapped_column(String(64), nullable=False)
    reporting_basis: Mapped[str] = mapped_column(String(16), nullable=False)
    is_derived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ExtractionRun(Base):
    """One execution of the extraction step against one document.

    Holds the AI-assisted workflow evidence the project doc requires: which
    prompt version, which fixture, what was sample-checked against source and
    what error rate was found.
    """

    __tablename__ = "extraction_run"
    __table_args__ = (
        CheckConstraint(
            "sample_checked IS NULL OR sample_size IS NULL OR sample_checked <= sample_size",
            name="ck_sample_within_size",
        ),
        CheckConstraint(
            "error_rate IS NULL OR (error_rate >= 0 AND error_rate <= 1)",
            name="ck_error_rate_range",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    source_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("source_document.id"), nullable=False
    )
    fixture_path: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(32), nullable=False)
    model_name: Mapped[str] = mapped_column(String(64), nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sample_size: Mapped[int | None] = mapped_column(Integer)
    sample_checked: Mapped[int | None] = mapped_column(Integer)
    error_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    notes: Mapped[str | None] = mapped_column(Text)

    source_document: Mapped[SourceDocument] = relationship(back_populates="extraction_runs")
