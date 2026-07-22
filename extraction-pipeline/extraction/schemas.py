"""Pydantic models mirroring the extraction prompt's output contract.

Fixture files are validated against these exactly as a live API response
would be. Validation is deliberately strict: a fixture that does not match
the contract is a defect in the extraction run and should fail loudly rather
than load partially.
"""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DocumentType = Literal[
    "information_document", "half_year_results", "presentation", "press_release"
]
ReportingEntity = Literal["ADF Farm Solutions Limited", "Senus PLC"]
ReportingBasis = Literal["company", "group", "mixed"]
Statement = Literal["profit_and_loss", "balance_sheet", "cash_flow", "narrative"]
DataClass = Literal["statement", "narrative", "approximation"]
LineItemUnit = Literal["eur", "percent", "count", "ratio"]
SignConvention = Literal["as_printed", "negated_label"]
ValidationStatus = Literal["valid", "flagged"]
SegmentType = Literal["channel", "geography", "product"]
TargetKind = Literal["threshold", "milestone"]
TargetUnit = Literal["eur", "percent", "ratio", "months", "count"]

# Period labels the loader can resolve. "unmapped" is accepted by the
# contract but skipped at load, per assumption A-16.
PeriodLabel = Literal["FY2024", "FY2025", "HY2025", "HY2026", "H2FY2025", "unmapped"]


class DocumentMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc_ref: str
    filename: str
    document_type: DocumentType
    publication_date: date
    reporting_entity: ReportingEntity
    reporting_basis: ReportingBasis
    page_count: int | None = None


class LineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(max_length=128)
    value: Decimal
    unit: LineItemUnit
    currency: str | None = Field(default=None, max_length=3)
    period_label: PeriodLabel
    statement: Statement
    data_class: DataClass
    page_number: int | None = None
    source_location: str | None = None
    sign_convention: SignConvention
    confidence: Decimal = Field(ge=0, le=1)
    validation_status: ValidationStatus
    validation_note: str | None = None

    @model_validator(mode="after")
    def currency_matches_unit(self) -> "LineItem":
        """Mirrors the ck_currency_matches_unit database constraint.

        Catching this here gives a readable error naming the offending label,
        rather than a constraint violation partway through a transaction.
        """
        if self.unit == "eur" and self.currency is None:
            raise ValueError(f"{self.label}: unit is eur but currency is null")
        if self.unit != "eur" and self.currency is not None:
            raise ValueError(
                f"{self.label}: unit is {self.unit} but currency is {self.currency}, expected null"
            )
        return self

    @model_validator(mode="after")
    def flagged_items_explain_themselves(self) -> "LineItem":
        """A flag without an explanation is not usable by a reviewer."""
        if self.validation_status == "flagged" and not self.validation_note:
            raise ValueError(f"{self.label}: flagged but no validation_note given")
        return self


class Segment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segment_type: SegmentType
    segment_name: str = Field(max_length=64)
    period_label: PeriodLabel
    revenue_share_pct: Decimal | None = Field(default=None, ge=0, le=100)
    revenue_value: Decimal | None = None
    customer_count: int | None = None
    avg_contract_value: Decimal | None = None
    page_number: int | None = None
    source_location: str | None = None
    confidence: Decimal = Field(ge=0, le=1)


class Target(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_type: str = Field(max_length=64)
    target_kind: TargetKind
    target_value: Decimal | None = None
    unit: TargetUnit
    target_period_label: str = Field(max_length=32)
    baseline_period_label: PeriodLabel | None = None
    baseline_value: Decimal | None = None
    page_number: int | None = None
    source_location: str | None = None
    confidence: Decimal = Field(ge=0, le=1)

    @model_validator(mode="after")
    def value_matches_kind(self) -> "Target":
        """Mirrors ck_target_value_matches_kind.

        A milestone carrying a numeric value invites a reader to compare an
        actual against a year. See validation defect V-02.
        """
        if self.target_kind == "threshold" and self.target_value is None:
            raise ValueError(
                f"{self.target_type}: threshold target has no target_value"
            )
        if self.target_kind == "milestone" and self.target_value is not None:
            raise ValueError(
                f"{self.target_type}: milestone target carries value {self.target_value}, "
                "expected null"
            )
        return self


class ExtractionResult(BaseModel):
    """A complete extraction run against one source document."""

    model_config = ConfigDict(extra="forbid")

    document: DocumentMeta
    line_items: list[LineItem] = Field(default_factory=list)
    segments: list[Segment] = Field(default_factory=list)
    targets: list[Target] = Field(default_factory=list)
    extraction_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def line_items_are_unique(self) -> "ExtractionResult":
        """Mirrors uq_line_item_identity.

        Duplicate label and period pairs would fail partway through the load
        transaction. Failing here names the duplicate instead.
        """
        seen: set[tuple[str, str]] = set()
        for item in self.line_items:
            key = (item.label, item.period_label)
            if key in seen:
                raise ValueError(
                    f"duplicate line item: {item.label} for {item.period_label}"
                )
            seen.add(key)
        return self
