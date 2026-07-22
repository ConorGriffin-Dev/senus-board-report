"""Raw extracted values. Never overwritten by computed values."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, uuid_pk
from app.models.enums import (
    DATA_CLASSES,
    LINE_ITEM_UNITS,
    SEGMENT_TYPES,
    SIGN_CONVENTIONS,
    STATEMENTS,
    VALIDATION_STATUSES,
)
from app.models.source import ReportingPeriod, SourceDocument


def _in(column: str, values: tuple[str, ...]) -> str:
    joined = ", ".join(f"'{v}'" for v in values)
    return f"{column} IN ({joined})"


class FinancialLineItem(Base):
    """A single figure as printed in a source document.

    The raw value is never corrected. Where a source figure is arithmetically
    inconsistent, validation_status is set to flagged and the discrepancy is
    described in validation_note. Inventory Finding 1 is the worked example:
    HY2025 cost of sales is stored as printed and flagged.

    sign_convention records whether the printed number carries its own sign.
    DOC-02 prints "Group operating loss 483,753" as a positive number in the
    profit and loss, and "-485,144" for the same underlying loss in the cash
    flow statement. Both are stored as printed. The metric layer negates
    negated_label rows before use, so the raw record stays faithful to the
    document while calculations stay correct.
    unit distinguishes monetary line items from percentages and counts stated
    in the source. currency is null for non-monetary items, enforced by
    constraint, so a percentage can never be rendered with a currency symbol.
    """

    __tablename__ = "financial_line_item"
    __table_args__ = (
        CheckConstraint(_in("statement", STATEMENTS), name="ck_statement"),
        CheckConstraint(_in("data_class", DATA_CLASSES), name="ck_data_class"),
        CheckConstraint(_in("validation_status", VALIDATION_STATUSES), name="ck_validation_status"),
        CheckConstraint(_in("sign_convention", SIGN_CONVENTIONS), name="ck_sign_convention"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_confidence_range"),
        CheckConstraint(_in("unit", LINE_ITEM_UNITS), name="ck_line_item_unit"),
        CheckConstraint(
            "(unit = 'eur' AND currency IS NOT NULL) OR (unit <> 'eur' AND currency IS NULL)",
            name="ck_currency_matches_unit",
        ),
        UniqueConstraint(
            "source_document_id", "reporting_period_id", "label", name="uq_line_item_identity"
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    source_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("source_document.id"), nullable=False
    )
    reporting_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reporting_period.id"), nullable=False
    )
    extraction_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("extraction_run.id"), nullable=False
    )

    label: Mapped[str] = mapped_column(String(128), nullable=False)
    # Four decimal places rather than two: DOC-01 states the implied share
    # price as 5.126, and rounding a raw source value at load would be a
    # silent alteration of the record.
    value: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(16), nullable=False, default="eur")
    currency: Mapped[str | None] = mapped_column(String(3), default="EUR")
    statement: Mapped[str] = mapped_column(String(32), nullable=False)

    page_number: Mapped[int | None] = mapped_column(Integer)
    source_location: Mapped[str | None] = mapped_column(Text)

    data_class: Mapped[str] = mapped_column(String(16), nullable=False, default="statement")
    confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    validation_status: Mapped[str] = mapped_column(String(16), nullable=False, default="valid")
    validation_note: Mapped[str | None] = mapped_column(Text)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    source_document: Mapped[SourceDocument] = relationship()
    reporting_period: Mapped[ReportingPeriod] = relationship()


class Segment(Base):
    """Aggregate segmentation figures.

    Replaces the provisional Customer entity from the first ER draft. No
    per-customer data exists in any source. segment_type distinguishes the
    three dimensions the sources actually disclose: channel, geography and
    product. FY2025 only, per A-12.
    """

    __tablename__ = "segment"
    __table_args__ = (
        CheckConstraint(_in("segment_type", SEGMENT_TYPES), name="ck_segment_type"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_segment_confidence"),
        CheckConstraint(
            "revenue_share_pct IS NULL OR (revenue_share_pct >= 0 AND revenue_share_pct <= 100)",
            name="ck_segment_share_range",
        ),
        UniqueConstraint(
            "reporting_period_id", "segment_type", "segment_name", name="uq_segment_identity"
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    source_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("source_document.id"), nullable=False
    )
    reporting_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reporting_period.id"), nullable=False
    )

    segment_type: Mapped[str] = mapped_column(String(16), nullable=False)
    segment_name: Mapped[str] = mapped_column(String(64), nullable=False)

    # Sources give percentage shares. Absolute values are derived, so they are
    # computed metrics rather than written back here. The column exists for
    # periods where an absolute figure is disclosed directly.
    revenue_share_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    revenue_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    customer_count: Mapped[int | None] = mapped_column(Integer)
    avg_contract_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)

    source_document: Mapped[SourceDocument] = relationship()
    reporting_period: Mapped[ReportingPeriod] = relationship()
