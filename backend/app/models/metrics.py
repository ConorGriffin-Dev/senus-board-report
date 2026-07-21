"""Derived values, traceability links, and forward-looking targets."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, uuid_pk
from app.models.enums import LINK_ROLES, METRIC_UNITS, TARGET_KINDS
from app.models.financial import FinancialLineItem
from app.models.source import ReportingPeriod, SourceDocument


def _in(column: str, values: tuple[str, ...]) -> str:
    joined = ", ".join(f"'{v}'" for v in values)
    return f"{column} IN ({joined})"


class ComputedMetric(Base):
    """A value derived from raw line items.

    caveat carries per-metric limitations rather than burying them in the
    frontend: DSCR is an interest coverage proxy (A-07), ROCE is distorted by
    the unexplained equity movement (A-08), cash runway excludes contingent
    consideration (A-06).
    """

    __tablename__ = "computed_metric"
    __table_args__ = (
        CheckConstraint(_in("unit", METRIC_UNITS), name="ck_metric_unit"),
        UniqueConstraint(
            "metric_type", "reporting_period_id", "calculation_version", name="uq_metric_identity"
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    metric_type: Mapped[str] = mapped_column(String(64), nullable=False)
    reporting_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reporting_period.id"), nullable=False
    )
    value: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(16), nullable=False)
    calculation_version: Mapped[str] = mapped_column(String(16), nullable=False, default="v1")
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # True where any input was itself derived rather than reported, so the UI
    # can distinguish a metric built on H2 FY2025 from one built on disclosures.
    is_derived_input: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    caveat: Mapped[str | None] = mapped_column(Text)

    reporting_period: Mapped[ReportingPeriod] = relationship()
    line_item_links: Mapped[list["MetricLineItemLink"]] = relationship(
        back_populates="computed_metric"
    )


class MetricLineItemLink(Base):
    """Traceability from a computed metric back to the raw figures behind it."""

    __tablename__ = "metric_line_item_link"
    __table_args__ = (
        CheckConstraint(_in("role", LINK_ROLES), name="ck_link_role"),
        UniqueConstraint(
            "computed_metric_id", "financial_line_item_id", "role", name="uq_link_identity"
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    computed_metric_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("computed_metric.id", ondelete="CASCADE"), nullable=False
    )
    financial_line_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("financial_line_item.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)

    computed_metric: Mapped[ComputedMetric] = relationship(back_populates="line_item_links")
    financial_line_item: Mapped[FinancialLineItem] = relationship()


class Target(Base):
    """Forward-looking Senus 2030 targets.

    Held separately from ComputedMetric so a target can never be rendered as
    though it were a reported actual.
    target_kind separates thresholds from milestones. A threshold is a level
    to reach, such as revenue CAGR of 50%, and carries a target_value. A
    milestone is an event expected by a date, such as EBITDA positive during
    FY2028, and has no meaningful numeric value. Encoding a year in
    target_value would let a UI compare EBITDA against 2028.
    """

    __tablename__ = "target"
    __table_args__ = (
        CheckConstraint(_in("unit", METRIC_UNITS), name="ck_target_unit"),
        CheckConstraint(_in("target_kind", TARGET_KINDS), name="ck_target_kind"),
        CheckConstraint(
            "(target_kind = 'threshold' AND target_value IS NOT NULL) "
            "OR (target_kind = 'milestone' AND target_value IS NULL)",
            name="ck_target_value_matches_kind",
        ),
        UniqueConstraint("target_type", "target_period_label", name="uq_target_identity"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    source_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("source_document.id"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_kind: Mapped[str] = mapped_column(String(16), nullable=False, default="threshold")
    target_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    unit: Mapped[str] = mapped_column(String(16), nullable=False)
    target_period_label: Mapped[str] = mapped_column(String(32), nullable=False)

    baseline_period_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reporting_period.id")
    )
    baseline_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))

    source_document: Mapped[SourceDocument] = relationship()
