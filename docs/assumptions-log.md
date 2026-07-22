# Assumptions Log

Every figure or treatment that is inferred, derived, or corrected rather than
read directly from a source document. Required by the project instructions:
anything inferred rather than sourced is stated explicitly.

Each entry records what was assumed, why, what the alternative was, and what
would change the decision.

---

## A-01: HY2025 cost of sales is treated as misstated in the source

**Source:** DOC-02, page 5, consolidated profit and loss, six months to
31 Dec 2024 column.

**Issue:** Turnover 340,931 less cost of sales 69,600 gives gross profit of
271,331. The document states gross profit of 272,331.

**Assumption:** The stated gross profit of 272,331 is correct and cost of
sales is misstated by 1,000. Correct cost of sales is 68,600.

**Basis:** Two independent checks corroborate the stated gross profit and
neither corroborates the stated cost of sales. Gross profit 272,331 less
administrative expenses 677,908 equals 405,577, exactly the stated group
operating loss. Gross profit 272,331 over turnover 340,931 gives 79.88%,
matching the stated gross margin of 79.8%. Cost of sales appears in no other
reconciling relationship in the document.

**Treatment:** The raw value 69,600 is ingested as printed with a validation
flag. All derived metrics use the stated gross profit. The raw value is never
overwritten, per the data model principle.

**Would change if:** The audited FY2026 annual report restates the HY2025
comparative, or the Company issues a correction.

---

## A-02: Annual and half-year figures are not on an identical basis

**Source:** DOC-01 section 7.1, page 25 (annual) and DOC-02, page 5
(half-year). Re-registration date from DOC-01 section 4.1.3, page 7.
Loamin acquisition date from DOC-01 section 5.3, page 14.

**Issue:** FY2024 and FY2025 are reported for ADF Farm Solutions Limited on
a company basis. HY2025 and HY2026 are reported for Senus PLC on a
consolidated group basis. The entity was renamed and re-registered as a PLC
on 17 Dec 2025. Loamin Limited was acquired 14 Nov 2025 and consolidated
from that date.

**Assumption:** The two sets are comparable for trend purposes but not
strictly like for like. The HY2025 comparative in DOC-02 is presented by the
Company itself as the comparative period, which implies the Company considers
it a valid basis for comparison.

**Basis:** DOC-02 note 1, page 7, states should be read in
conjunction with the annual statements for the year ended 30 June 2025,
which is the Company directing readers to treat them as a continuous series.

**Treatment:** reporting_entity and reporting_basis stored as attributes on
SourceDocument. Any view mixing annual and half-year figures displays the
caveat. Growth rates that cross the boundary are computed but labelled.

**Would change if:** The FY2026 annual report restates prior periods on a
consistent group basis.

---

## A-03: H2 FY2025 revenue is derived by subtraction

**Source:** DOC-01 section 7.1, page 25 (FY2025 turnover) and DOC-02,
page 5 (HY2025 turnover).

**Derived value:** 496,060.

**Method:** FY2025 turnover 836,991 less HY2025 turnover 340,931.

**Assumption:** The two figures cover contiguous, non-overlapping periods
within the same financial year and are additive.

**Basis:** FY2025 runs 1 Jul 2024 to 30 Jun 2025. HY2025 runs 1 Jul 2024 to
31 Dec 2024. The residual is 1 Jan 2025 to 30 Jun 2025.

**Limitation:** Inherits the basis mismatch in A-02, since the annual figure
is company basis and the half-year figure is group basis. For FY2025 the
group had one dormant UK subsidiary and no acquisitions, so the difference
is likely immaterial, but this is an inference not a disclosure.

**Treatment:** Stored as a ComputedMetric, never as a raw FinancialLineItem,
with traceability links to both inputs. Labelled as derived in the UI.

**Purpose:** Quantifies the seasonality the Company describes qualitatively.
H1 represents 40.7% of FY2025 revenue against H2 at 59.3%.

---

## A-04: EBITDA is computed as operating loss plus depreciation only

**Source:** DOC-02, pages 5 and 6.

**Applies to:** HY2025 and HY2026.

**Assumption:** No amortisation charge is included in the period, so EBITDA
equals operating profit plus depreciation with no separate amortisation
add-back.

**Basis:** The HY2026 cash flow statement, DOC-02 page 6, lists depreciation of 10,014 as the
only non-cash adjustment to the loss for the period alongside interest. No
amortisation line appears in either the profit and loss or the cash flow,
despite development costs of 239,765 sitting on the balance sheet.

**Resulting figures:**
- HY2026: operating loss 483,753 plus depreciation 10,014 gives EBITDA of
  -473,739. Margin -133.5%.
- HY2025: operating loss 405,577 plus depreciation 10,016 gives EBITDA of
  -395,561. Margin -116.0%.

Both reconcile exactly to the subtotal line in the cash flow statement,
which is a strong corroboration.

**Limitation:** Development costs were newly recognised in HY2026 following
the Loamin acquisition. If amortisation on those costs begins in H2 FY2026,
EBITDA and operating loss will diverge in future periods.

**Would change if:** Amortisation is disclosed separately in a future period.

---

## A-05: Annual EBITDA is not computed

**Source:** DOC-01 section 7.1, page 25. Depreciation absent.

**Assumption:** EBITDA is not presented for FY2024 or FY2025.

**Basis:** Depreciation is not disclosed for either annual period in DOC-01.
Computing annual EBITDA would require assuming a depreciation figure, most
plausibly by annualising the half-year charge of approximately 10,000. That
would be inventing a number and presenting it alongside audited figures.

**Treatment:** EBITDA metrics carry an availability scope of half-year
periods only. The UI shows the metric as unavailable for annual periods
rather than rendering a gap as zero or silently interpolating.

**Would change if:** The FY2026 annual report discloses depreciation, at
which point annual EBITDA becomes computable for FY2026 onward.

---

## A-06: Cash runway is computed on HY2026 operating burn

**Source:** DOC-02, pages 6 to 7 (cash flow) and note 4, page 8
(contingent consideration).

**Computed value:** Approximately 10.7 months from 31 Dec 2025.

**Method:** Closing cash 735,189 divided by monthly operating cash burn.
Net cash used in operating activities for the six months was 410,291,
giving a monthly burn of 68,382.

**Assumptions:** Burn continues at the HY2026 rate; no further capital is
raised; the contingent consideration of 850,000 is excluded.

**Basis for excluding contingent consideration:** DOC-02 note 4, page 8, states it is
entirely performance-linked and payable only if specified performance
targets are achieved. It is not a scheduled cash outflow.

**Limitation, material:** If the contingent consideration crystallises it
exceeds the cash balance. The runway figure must be presented alongside that
exposure, not in isolation. A runway metric that ignores an 850,000
contingent liability against a 735,189 cash balance is misleading.

**Also note:** HY2026 burn is not necessarily representative. The period
included one-off listing and acquisition costs, and the Company describes a
weather-delayed soil sampling season that suppressed revenue.

---

## A-07: DSCR is presented as an interest coverage proxy

**Source:** DOC-02, page 5 (interest payable) and page 6 (creditors due
after more than one year).

**Assumption:** A true debt service coverage ratio cannot be computed. What
is presented is EBITDA over interest payable, labelled as such.

**Basis:** Interest payable (1,391 HY2026) and bank debt (76,474) are
disclosed, but no principal repayment schedule, loan term, or amortisation
profile is published in any source document. Debt service requires principal
plus interest.

**Treatment:** Presented with the limitation stated on the metric itself. The
resulting ratio is negative because EBITDA is negative, so its analytical
value is limited and the report should say so rather than displaying a
negative number without context.

**Would change if:** A loan schedule is disclosed in the FY2026 annual
report.

---

## A-08: Unexplained equity movement is flagged, not adjusted

**Source:** DOC-01 section 7.1, page 25 (position at 30 Jun 2025) and
DOC-02, pages 5 to 6 (position at 31 Dec 2025).

**Issue:** Between 30 Jun 2025 and 31 Dec 2025, retained earnings move from
-865,681 to +236,081, a positive swing of 1,101,762, despite a loss for the
period of 485,144. Share premium falls from 849,963 to 300,000 and called up
share capital rises from 144 to 25,000.

**Assumption:** This reflects a capital reorganisation on re-registration as
a PLC. No adjustment is made to any figure.

**Basis:** The pattern of share premium reduction with a corresponding
retained earnings increase is characteristic of a capital reduction. The
timing coincides with re-registration on 17 Dec 2025. However, no note in
DOC-02 explains it, so this is inference.

**Treatment:** No figures adjusted. A flag is attached to ROCE and any
equity-based metric. Recorded as an open question for the FY2026 annual
report.

**Impact:** ROCE across the boundary is not meaningful. Capital employed
moves from negative to positive for reasons partly unrelated to trading.

---

## A-09: Bookings and pipeline figures are approximations

**Values:** Approximately 700,000 closed across 21 enterprise customers,
approximately 500,000 open pipeline, 10 deals worth approximately 425,000 in
Nov and Dec 2025, Biochar contract valued at 300,000.

**Source:** DOC-02, page 1 (Highlights), page 3 (Commercial Progress and
Pipeline & Outlook).

**Assumption:** These are management estimates, not audited figures, and are
treated as a distinct class of data.

**Basis:** DOC-02 states them in narrative prose on pages 1 and 3, not on the financial statements at pages 5 to 7,
using the word
approximately, not in the financial statements. They are unaudited and
undefined, with no stated basis for what counts as closed or as pipeline.

**Treatment:** Extracted with a low confidence score. Visually distinguished
from statement-derived figures in the UI. Not used as an input to any
computed financial metric.

---

## A-10: Month on month growth is out of scope

**Source:** Absence across DOC-01, DOC-02 and DOC-03. Metric requested in
DOC-06, assignment brief page 3.

**Assumption:** MoM growth is not presented anywhere in the report.

**Basis:** No monthly data exists in any source document. Senus reports on a
half-year and annual basis, as required of a Euronext Access issuer. The
finest granularity available is six months.

**Treatment:** The assignment brief lists MoM as an example growth metric.
The report substitutes half-year-on-half-year and period-over-period growth
and states the reason. Presenting a fabricated monthly series would be
inventing data.

---

## A-11: Goodwill figure discrepancy resolved to the balance sheet

**Source:** DOC-02, page 5 (balance sheet) and note 4, page 8.

**Issue:** DOC-02 balance sheet states goodwill of 669,550. Note 4 states
669,500.

**Assumption:** The balance sheet figure of 669,550 is correct.

**Basis:** The balance sheet figure participates in the fixed assets
subtotal of 951,321. Checking: 669,550 plus 239,765 plus 42,006 equals
951,321. The note figure does not reconcile.

**Treatment:** Balance sheet figure used. Note figure flagged.

---

## A-12: FY2025 segmentation is not carried forward to HY2026

**Source:** DOC-01 sections 5.1.1 and 7.3, pages 11 to 12 and 26.
DOC-03, pages 10 and 11. Absent from DOC-02.

**Assumption:** Channel mix, geographic mix, customer counts and ACV are
presented for FY2025 only and are not extrapolated to the half-year periods.

**Basis:** Segmentation is disclosed for FY2025 in DOC-01 and DOC-03. No
equivalent breakdown is published for HY2025 or HY2026. The 21 enterprise
customers referenced in DOC-02 relate to deals closed in the period, which
is a different measure from customers served.

**Treatment:** Segmentation metrics carry an availability scope of FY2025.
The UI does not imply currency for these figures and labels the period
clearly.

---

## A-13: Point-in-time facts are attributed to HY2026, not FY2025

**Source:** DOC-01, various sections. Five items: private placement gross
proceeds, post money enterprise valuation, implied share price on admission,
issued share capital, employee headcount.

**Issue:** These are facts as at Admission on 22 December 2025, which falls
in HY2026. The extraction attributed all five to FY2025 because DOC-01 is
dated December 2025 and presents them as current. `reporting_period_id` is
not nullable, so every figure must belong to some period.

**Assumption:** All five are reattributed to HY2026 at load, with the
reattribution recorded in `validation_note` on each row.

**Alternatives rejected:** Adding a point-in-time period entity would be
disproportionate for five items and would complicate every period-scoped
query. Skipping them would lose the private placement, which is material
context for the cash position.

**Basis:** 22 December 2025 falls within the six months to 31 December 2025.
DOC-03 independently attributes the private placement to that period, which
corroborates the treatment.

**Treatment:** Loader reattributes and logs. Raw values unchanged.

---

## A-14: DOC-01 is authoritative for targets and segments

**Issue:** DOC-01 and DOC-03 both carry the five Senus 2030 targets and
overlapping segment data. `Target` is unique on target type and target
period; `Segment` is unique on reporting period, segment type and segment
name. Neither constraint includes the source document, so loading both
fixtures collides.

**Assumption:** DOC-01 wins. DOC-03 duplicates are skipped at load and the
skip is logged.

**Basis:** DOC-01 is the listing document, prepared under Director
responsibility and reviewed by the Listing Sponsor and Euronext. DOC-03 is a
marketing presentation. Where the two agree, which they do on every
overlapping figure, the choice is immaterial to values and matters only for
provenance. DOC-01 also carries fuller data: three product contract values
against two, and full channel segmentation which DOC-03 lacks entirely.

**Alternative rejected:** Widening the constraints to include source
document would store the same target twice and push de-duplication to query
time, where it would be easier to get wrong.

**Consequence:** DOC-03's corroboration is recorded in its validation notes
rather than in the database. The database shows one source per target; the
fact that a second source agrees is documented but not queryable.

---

## A-15: The private placement is an explicit exception to A-14

**Issue:** DOC-01 attributes the private placement to FY2025, DOC-03 to
HY2026. Same event, contradictory attribution. A blanket DOC-01-wins rule
would take the wrong one.

**Assumption:** HY2026 is correct, per A-13. The DOC-01 record is
reattributed rather than the DOC-03 record being preferred.

**Basis:** The placement completed in December 2025. DOC-01's attribution
reflects the document's own publication context rather than the event date.

**Treatment:** Handled by the A-13 reattribution rule, which applies to the
DOC-01 record. The DOC-03 record is then a duplicate on the same period and
is skipped under A-14. Net effect is one row, correctly attributed, sourced
to DOC-01.

**Note:** This is the first contradiction between two fixtures. The
resolution is recorded rather than silently applied, because a loader that
silently reconciles conflicting sources is exactly the failure mode the
raw-never-overwritten principle exists to prevent.

---

## A-16: Unmapped period items are not loaded

**Source:** DOC-03, the 2023 fundraise of 800,000.

**Issue:** The figure falls in FY2023. No FY2023 reporting period exists,
because no FY2023 financial data is available from any source. The
extraction correctly recorded `period_label` as `unmapped`.

**Assumption:** Items with an unmapped period are skipped at load and the
skip is logged with the reason.

**Basis:** Seeding a period with no financial data attached would create an
empty column in every period-scoped view. The figure is corporate history
rather than reportable financial data.

**Treatment:** Loader skips and logs. The figure remains in the committed
fixture, so it is not lost, only not loaded.

---

## A-17: No document parser or cleaner modules are built

**Decision:** The `parsers/` and `cleaners/` directories described in the
original architecture are not implemented, and the empty directories are
removed.

**Basis:** Under the fixture-based AI method in project instructions section
3.1, the model reads the source PDF directly through the chat interface.
Nothing in the pipeline parses a document. Building pdfplumber and pandas
modules that no code path calls would be dead code, which the project's own
code style rules prohibit.

**What is lost:** The architecture diagram shows a document parser and data
cleaner feeding the extraction service. Those boxes describe the live-API
architecture that the swap point would enable, not the fixture-based path
actually in use. The diagram is accurate about intent and inaccurate about
current implementation.

**Treatment:** The README and the system architecture diagram must both
state that parsing happens outside the codebase under the fixture method,
and that the parser and cleaner stages would be needed if the swap point
were wired to a live API. Directories removed rather than left empty.

**Would change if:** A live API key were introduced, at which point document
text would need extracting in code before the model call.
