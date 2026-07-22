"""Load-time rules that resolve problems found during fixture validation.

Each rule maps to a numbered entry in docs/assumptions-log.md. Keeping them
here rather than inline in the loader means the set of deviations between
fixture and database is enumerable in one place, and a reviewer can check
each against its logged justification.
"""

# A-13: facts stated as at Admission (22 December 2025) fall in HY2026, not
# FY2025. DOC-01 attributed them to FY2025 because that document was
# published in December 2025 and presents them as current.
POINT_IN_TIME_REATTRIBUTION = {
    ("DOC-01", "Private placement gross proceeds", "FY2025"): "HY2026",
    ("DOC-01", "Post money enterprise valuation", "FY2025"): "HY2026",
    ("DOC-01", "Implied share price on admission", "FY2025"): "HY2026",
    ("DOC-01", "Issued share capital", "FY2025"): "HY2026",
    ("DOC-01", "Employee headcount", "FY2025"): "HY2026",
}

REATTRIBUTION_NOTE = (
    "Period reattributed at load from {original} to {reattributed}. "
    "Stated as at Admission on 22 December 2025, which falls in HY2026. "
    "See assumption A-13."
)

# A-14: DOC-01 is the listing document prepared under Director
# responsibility; DOC-03 is a marketing presentation. Where they overlap on
# targets and segments they agree on every value, so this affects provenance
# rather than figures.
AUTHORITATIVE_FOR_TARGETS = "DOC-01"
AUTHORITATIVE_FOR_SEGMENTS = "DOC-01"

# A-16: no FY2023 reporting period exists, because no FY2023 financial data
# is available. The 2023 fundraise stays in the committed fixture but is not
# loaded.
SKIP_UNMAPPED_PERIODS = True


def reattributed_period(doc_ref: str, label: str, period_label: str) -> str | None:
    """Return the corrected period label, or None if no rule applies."""
    return POINT_IN_TIME_REATTRIBUTION.get((doc_ref, label, period_label))


def append_note(existing: str | None, addition: str) -> str:
    """Append to a validation note without discarding what extraction said."""
    return f"{existing} {addition}" if existing else addition
