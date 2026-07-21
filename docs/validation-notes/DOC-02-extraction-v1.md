# Validation Notes: DOC-02 Extraction, prompt v1

Fixture: `fixtures/extraction/DOC-02.json`
Prompt: `prompts/extraction_v1.md` (v1)
Source: Senus PLC Half Year Results, 6 months ended 31 December 2025
Extraction method: manual, via Claude.ai chat interface with the PDF attached
Validated: 2026-07-21

## Method

Every extracted figure was checked back against the source document rather
than a sample. The fixture contains 91 line items and 2 targets, which is
small enough that a full census is achievable and gives a stronger result
than a sample would.

Each item was checked on four dimensions:

1. **Value** matches the figure printed in the source
2. **Period attribution** matches the correct column of the statement
3. **Location** matches the stated page and section
4. **Classification** is correct for statement, data_class and sign_convention

Checking period attribution separately matters because a transposed
comparative column is the highest-consequence error available in this task,
and it produces a figure that is individually correct but wrong in context.

## Results

| Dimension | Checked | Errors | Error rate |
|---|---|---|---|
| Value transcription | 93 | 0 | 0.0% |
| Period attribution | 93 | 0 | 0.0% |
| Page and location reference | 93 | 0 | 0.0% |
| Classification | 93 | 2 | 2.2% |
| **Overall** | **93** | **2** | **2.2%** |

Zero transcription errors across 91 line items and 2 targets. Two
classification defects, detailed below. Both are schema misuse rather than
misreading of the source, and neither affects a figure's value or period.

## Defects found

### V-01: Percentage values carry a currency code

**Items:** "Gross margin (as stated)" for HY2026 and HY2025.

**Problem:** Both carry `"currency": "EUR"` while holding a percentage value
(81.70 and 79.80). The currency field is meaningless for a percentage, and a
naive consumer reading currency alongside value would render "€81.70".

**Cause:** The prompt's output schema makes `currency` unconditional on line
items and does not describe how to represent a non-monetary figure. The
`FinancialLineItem` model has the same gap: `currency` is `nullable=False`
with a default of EUR, and there is no unit column.

**Severity:** Low as it stands, because only two items are affected and both
are cross-check values rather than metric inputs. Higher if left, because any
future extraction of a percentage or count would repeat it.

**Resolution:** Deferred, with a decision needed. Three options:

- Add a `unit` column to `FinancialLineItem` mirroring the one on
  `ComputedMetric`, and make `currency` nullable
- Exclude stated percentages from extraction entirely, since the pipeline
  computes margins from the underlying figures anyway
- Keep them as they are and rely on `data_class` of narrative to signal that
  the value needs interpretation

The first is cleanest but adds a migration. The second loses a genuinely
useful cross-check: the stated 79.8% margin is one of the two pieces of
evidence that identifies the cost of sales error. Recommendation is the
first.

### V-02: Target value encodes a year in a numeric field

**Item:** Target `ebitda_positive`.

**Problem:** `target_value` is 2028.0 with `unit` of count. The target is not
a quantity of 2028 anything; it is a milestone with a date. The value field
is being used to carry a year because the schema has nowhere else to put it.

**Cause:** The `Target` model assumes every target is a numeric threshold
(revenue CAGR of 50%, ACV above 50,000, customers above 100). A
date-milestone target does not fit that shape.

**Severity:** Low in isolation, but it will produce a wrong render. Any UI
treating `target_value` as a number to compare against an actual would
compare EBITDA to 2028.

**Resolution:** Deferred, with a decision needed. Either add a
`target_kind` discriminator to `Target` separating threshold targets from
milestone targets, or exclude milestone targets from the table and present
them as narrative context only. The EBITDA-positive-by-FY2028 milestone is
genuinely useful board context, so excluding it loses something.

## Findings confirmed, not defects

The extraction flagged eight items. All eight flags were verified as correct
and appropriate.

**The systematic 1 euro subtotal discrepancies.** Six subtotals are off by
exactly 1 against the sum of their components: total current assets both
periods, net current assets HY2025, total assets less current liabilities
HY2026, net assets HY2026, equity attributable to owners HY2025, and closing
cash HY2026. Each was recomputed by hand and each is off by exactly 1 in the
direction consistent with rounding half-up from figures held in cents. This
is a presentational artifact of the source, not an extraction error and not a
substantive misstatement. Recording it rather than absorbing it is the
correct behaviour: the pattern is only visible because every subtotal was
checked, and a reader who spot-checks one subtotal deserves to find the
explanation already recorded.

**The HY2025 cost of sales discrepancy of 1,000.** Verified as a genuine
inconsistency in the source and materially different in kind from the
rounding artifacts. Turnover 340,931 less cost of sales 69,600 gives 271,331
against a stated gross profit of 272,331. The stated gross profit is
corroborated twice over: it reconciles with the operating loss (272,331 less
677,908 equals the stated 405,577), and it produces the stated 79.8% margin
(272,331 over 340,931 equals 79.88%). Cost of sales reconciles with nothing.
The extraction correctly stored 69,600 as printed and identified 68,600 as
the probable correct figure without altering the record.

**The goodwill conflict.** Balance sheet 669,550 against note 4's 669,500.
Verified: the balance sheet figure reconciles with the fixed assets subtotal
(669,550 plus 239,765 plus 42,006 equals 951,321). The note figure does not.
Correctly resolved to the balance sheet.

**The retained earnings movement.** Verified as unexplained in the source.
Notes 1 to 5 on pages 7 and 8 do not address it. Correctly flagged rather
than rationalised.

**The share issuance difference.** Cash flow shows 1,138,683 against
narrative references to 1.1m gross proceeds. Verified as present in the
source and unexplained. Correctly extracted as both figures rather than
reconciled.

## Judgement calls reviewed

Four extraction decisions involved judgement rather than transcription. All
four were reviewed and stand.

**Unlabelled subtotals were given labels.** Five subtotals have no label in
the source. Extraction assigned descriptive labels and reduced confidence to
0.95, noting the assignment on each item. This is the right trade: the
alternative is either dropping the subtotals or inventing an empty label, and
the assigned labels are conventional accounting terms rather than
interpretation.

**Cost lines were marked negated_label.** Cost of sales, administrative
expenses, distribution costs, interest payable and tax expense are printed as
positive numbers under labels that denote expense. Marking them
`negated_label` is correct and is precisely why that column exists. The
metric layer must negate them; storing them negated at ingest would have
been a silent correction.

**Balance sheet creditors were marked as_printed.** Creditors, contingent
consideration and net current assets are printed with explicit minus signs,
so they carry their own sign and `as_printed` is correct. Note the
inconsistency in the source itself: the profit and loss uses label-implied
signs while the balance sheet uses explicit signs. Handling both correctly is
the point of the field.

**The 21 enterprise customers figure was not extracted as a customer count.**
Correct. It counts customers with deals closed in the period, which is a
different measure from customers served. Extracting it as a customer count
would invite comparison against the FY2025 figure of 36 enterprise customers
served, which would be a false comparison.

## Limitations of this validation

Stated plainly, because they bear on how much weight the 0% transcription
error rate deserves.

**The validation was performed by the same model, in the same session, that
produced the extraction.** This is self-verification. It reliably catches
transcription slips and arithmetic inconsistencies, since those are checkable
against the document text. It is much weaker at catching systematic
misunderstandings, because an error of interpretation in extraction is likely
to be repeated in validation. The two classification defects were found, but
both were found by checking the fixture against the schema rather than
against the document, which is a different kind of check.

**A stronger validation would be independent.** Either a second extraction
run in a fresh session compared against this one, or a human check of a
sample against the PDF. The second of these is cheap for a document this
size and would meaningfully raise confidence in the result.

**The source document is a press release, not audited statements.** DOC-02
presents unaudited interim figures. Extraction fidelity to the document is
what was measured here. It says nothing about the accuracy of the underlying
figures.

## Conclusion

The extraction is fit for use. Zero transcription errors across 93 items,
correct period attribution throughout, and all eight source inconsistencies
correctly identified and flagged rather than absorbed.

Two schema defects need resolving before further extraction runs, since both
would recur. Neither blocks loading this fixture.
