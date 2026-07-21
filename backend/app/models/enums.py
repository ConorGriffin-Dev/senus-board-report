"""Allowed values for discriminator columns, enforced via CHECK constraints."""

DOCUMENT_TYPES = ("information_document", "half_year_results", "presentation", "press_release")

REPORTING_ENTITIES = ("ADF Farm Solutions Limited", "Senus PLC")
REPORTING_BASES = ("company", "group", "mixed")

PERIOD_TYPES = ("annual", "half_year")

STATEMENTS = ("profit_and_loss", "balance_sheet", "cash_flow", "narrative")

# Distinguishes audited statement figures from prose approximations (A-09).
DATA_CLASSES = ("statement", "narrative", "approximation")

VALIDATION_STATUSES = ("valid", "flagged", "failed")

SEGMENT_TYPES = ("channel", "geography", "product")

METRIC_UNITS = ("eur", "percent", "ratio", "months", "count")

LINK_ROLES = ("numerator", "denominator", "prior_period", "current_period", "component")

# as_printed: the number carries its own sign.
# negated_label: a positive number represents a loss or outflow because the
# label says so, e.g. "Group operating loss 483,753". The metric layer must
# negate these before use.
SIGN_CONVENTIONS = ("as_printed", "negated_label")
