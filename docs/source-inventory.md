# Source Document Inventory

Completed: Step 1 of the build plan. This document records what source
material exists, what financial data it genuinely contains, and which
assignment metrics are therefore supportable. Finalised before any schema or
metric work, so the data model is built against real fields rather than
assumed ones.

## Documents

| ID | Document | Date | Pages | Retrieved | Location |
|---|---|---|---|---|---|
| DOC-01 | Senus PLC Information Document (Euronext listing prospectus) | Dec 2025 | 45 | 18 Jul 2026 | https://live.euronext.com/sites/default/files/2025-12/SENUS%20PLC%20-%20Information%20Document.pdf |
| DOC-02 | Half Year Results, 6 months ended 31 Dec 2025 | 19 Mar 2026 | 9 | 18 Jul 2026 | Senus IR portal, https://app.assiduous.tech/investor-relations/senus. Filename: Senus_HalfYearResultsDec2025_PR_V19032026 FINAL clean.pdf |
| DOC-03 | Senus short corporate presentation | 19 Mar 2026 | 14 | 18 Jul 2026 | Senus IR portal, https://app.assiduous.tech/investor-relations/senus. Filename: Senus short corporate presentation 19032026.pdf |
| DOC-04 | Direct Listing press release | 18 Dec 2025 | 1 | 18 Jul 2026 | https://senus.com/senus-plc/ |
| DOC-05 | Euronext listing announcement | 22 Dec 2025 | 1 | 18 Jul 2026 | https://www.euronext.com/en/about/media/euronext-press-releases/senus-lists-euronext-access |
| DOC-06 | Assiduous Technology Graduate Assessment brief | 2026 | 5 | Supplied | Assignment brief. Defines required metric categories and deliverables. Not a financial data source. |

DOC-02 and DOC-03 are the extraction pipeline's working source documents.
DOC-01 is the second-priority source. DOC-04 and DOC-05 corroborate only and
contain no figures not present elsewhere. DOC-06 defines scope, not data.

### Retrieval notes

The Senus investor relations portal at app.assiduous.tech is a client-side
rendered application. Its content does not appear in the served HTML and
cannot be retrieved programmatically or by a plain HTTP fetch. DOC-02 and
DOC-03 were downloaded manually through a browser on 18 Jul 2026, and the
portal listed exactly those two items on that date. Any later addition to
the portal is outside this inventory.

DOC-02 was not located anywhere in the public web at the time of retrieval.
Senus is small enough that Euronext Access announcements are not picked up
by news aggregators, so the IR portal is the only route to it. This is worth
stating because it means the inventory cannot be reproduced by search alone.

DOC-01 is publicly hosted by Euronext and is retrievable without
authentication.

### Source documents are not committed to this repository

Standing decision. The source PDFs are excluded from version control via
`.gitignore` at `extraction-pipeline/source-docs/`. They are Senus PLC
investor communications and remain the Company's material, so they are not
republished here.

Consequence: the extraction run cannot be reproduced end to end from a clean
clone. This is deliberate and mitigated as follows.

- The extraction outputs are committed as fixture files under `fixtures/`,
  so the pipeline downstream of the model call runs against real data
  without the PDFs present.
- Every extracted figure carries a source reference to document, page and
  location, so any value can be traced back to a specific place in a
  specific document and verified by a reviewer who obtains it independently.
- The figure-level source reference table above records where each class of
  data sits, so a reviewer knows what to check and where.
- Validation notes in `docs/validation-notes/` record the sample checked and
  the error rate found at the time of extraction.
- DOC-01 is publicly retrievable at the URL given, so the annual figures are
  independently verifiable by anyone.

To obtain DOC-02 and DOC-03, retrieve them from the Senus investor relations
portal at the URL given above and place them in
`extraction-pipeline/source-docs/`. They are not obtainable by web search.

### Figure-level source references

Extraction must populate a source reference for every line item. The
locations below are established during inventory so the extraction prompt
has a known target rather than inferring position.

| Data | Document | Location |
|---|---|---|
| FY2024 and FY2025 summary financials | DOC-01 | Section 7.1, Summary Financial Information, page 25 |
| FY2025 narrative figures (admin expenses, trade debtors and creditors, term loan) | DOC-01 | Section 7.1, Profit and Loss / Balance Sheet / Cash Flow commentary, pages 26 |
| R&D expenditure percentages | DOC-01 | Section 5.3.1, page 23 |
| Channel split and customer counts | DOC-01 | Section 5.1.1, Senus Commercial Model and Customers, pages 11 to 12 |
| Geographic split | DOC-01 | Section 5.1.1, Senus Territories, page 14 |
| Average annual contract value by product | DOC-01 | Section 7.3, Key Performance Indicators, page 26 |
| FY2030 targets | DOC-01 | Section 7.3, page 26. Also DOC-03 page 11 |
| Capital structure and shareholdings | DOC-01 | Section 12.1, page 30 |
| Related party and Director loans | DOC-01 | Section 13, page 31 |
| HY2026 and HY2025 profit and loss | DOC-02 | Consolidated Profit and Loss Account, page 5 |
| HY2026 and HY2025 balance sheet | DOC-02 | Consolidated Balance Sheet, pages 5 to 6 |
| HY2026 and HY2025 cash flow | DOC-02 | Consolidated cash flow statement, pages 6 to 7 |
| Depreciation | DOC-02 | Cash flow statement, page 6 |
| Bookings and pipeline figures | DOC-02 | Highlights (page 1) and Pipeline & Outlook (page 3). Prose, not statements |
| Biochar contract value | DOC-02 | Commercial Progress, page 3 |
| Goodwill and contingent consideration | DOC-02 | Balance sheet pages 5 to 6, and note 4 page 8 |
| Basis of preparation, FRS 102 | DOC-02 | Note 1, page 7 |
| Customer names and logos | DOC-03 | Page 5 |
| FY2030 targets restated | DOC-03 | Page 11 |
## Financial data available

### Annual, from DOC-01 section 7.1

Turnover, gross profit, operating profit/(loss), profit/(loss) before tax,
profit/(loss) after tax, net (liabilities)/assets, retained earnings,
operating cash flow, investing cash flow, financing cash flow, net change in
cash, opening cash, closing cash. Both FY2024 and FY2025.

Additional annual figures stated in narrative prose rather than tables, so
extraction confidence should be scored lower for these: administrative
expenses 1,286,058 (FY2025), trade debtors 66,990 / 142,361, trade creditors
55,246 / 26,768, new SBCI-backed term loan 100,000, R&D expenditure at 17%
of revenue (FY2025) and 22% (FY2024), annual office rent 41,500.

### Half-year, from DOC-02

Full consolidated statements, all with prior-period comparatives:

- Profit and loss: turnover, cost of sales, gross profit, distribution
  costs, administrative expenses, other operating income, group operating
  loss, interest payable, loss before taxation, tax expense, loss for period
- Balance sheet: goodwill, development costs, tangible assets, debtors, cash,
  creditors under one year, contingent consideration, net current assets,
  creditors over one year, net assets, share capital, share premium,
  retained earnings
- Cash flow: loss for period, interest adjustment, depreciation, movements in
  working capital, cash used in operations, interest paid, net operating cash
  flow, investing cash flow, loans received/repaid, share issuance, net
  financing cash flow, net change in cash, opening and closing cash

Depreciation being disclosed (10,014 HY2026, 10,016 HY2025) is what makes
EBITDA computable rather than assumed. It is not disclosed for FY2024 or
FY2025.

### Segmentation, from DOC-01 and DOC-03

FY2025 only. No segmentation is disclosed for the half-year periods.

- By channel: Enterprise 69% of sales, 36 customers; Independent 4%, 98
  customers; R&D 27%, 4 customers. Total 138, reconciles to headline figure.
- By geography: Ireland approximately 78%, rest of world approximately 22%.
  FY2024 comparative: less than 5% non-Ireland.
- Average annual contract value by product: Soil 12,309, Terrain 21,524,
  ERA 58,900.

### Bookings and pipeline, from DOC-02

First period in which bookings data is quantified at all.

- Approximately 700,000 closed across 21 enterprise customers in HY2026
- Approximately 500,000 open pipeline
- 10 commercial deals closed in Nov and Dec 2025, combined value
  approximately 425,000
- Biochar contract with Department of Agriculture, Food and the Marine,
  multiannual, valued at 300,000

These are stated as approximations in prose. They must be flagged as
low-confidence and clearly distinguished from audited figures in the UI.

### Capital structure

Issued share capital 2,561,332 shares of 0.01 nominal. Admission price
5.126. Market capitalisation at admission 13,130,000. Private placement
gross proceeds 1,100,000, share issuance recorded as 1,138,683 in the
HY2026 cash flow. Bank debt 76,474 at 31 Dec 2025. Contingent consideration
850,000 on the Loamin acquisition, performance-linked. Goodwill on
acquisition 669,550 (note 4 states 669,500, see assumptions log).

### Targets, from DOC-01 and DOC-03

Revenue CAGR of no less than 50% across FY2026 to FY2030. Enterprise
customers above 100 by FY2030 (36 in FY2025). Average enterprise ACV above
50,000 by FY2030. Ireland below 50% of revenue by FY2030 (78% in FY2025).
EBITDA positive during FY2028.

Targets are forward-looking statements, not financial data. They belong in
the report as benchmark context against actuals, and must be visually
distinguished from reported figures.

## Metric feasibility

Assessed against the metric categories requested in the assignment brief.

### Supported by source data

| Metric | Periods | Notes |
|---|---|---|
| Revenue growth, period on period | FY24 to FY25, HY25 to HY26 | 21.6% and 4.1% respectively |
| Gross margin | All four | 62.8%, 77.5%, 79.8%, 81.7% |
| Operating margin | All four | |
| EBITDA and EBITDA margin | HY2025, HY2026 only | Depreciation disclosed for half-years only |
| Cost breakdown | All four | Cost of sales and administrative expenses split available at half-year; annual is less granular |
| Working capital | HY2025, HY2026 | Debtors and creditors disclosed on the balance sheet |
| Cash movement and closing cash | All four | |
| Cash runway | HY2026 | Approximately 10.7 months on HY2026 operating burn, before contingent consideration |
| Customer count, total and by channel | FY2025 | |
| Channel revenue mix | FY2025 | |
| Geographic revenue mix | FY2024, FY2025 | |
| Average annual contract value | FY2025 | By product line |
| Bookings and pipeline | HY2026 | Approximations stated in prose |
| Seasonality (H1 versus H2 split) | FY2025 | Via the derived H2 figure |

### Supported with stated limitations

**Debt service coverage ratio.** Interest payable (1,391 HY2026) and bank
debt (76,474) are disclosed, but no principal repayment schedule is
published. Computable as an interest coverage proxy only. Given operating
losses the ratio is negative and its analytical value is limited. Include
with the limitation stated explicitly on the metric card rather than
silently presenting a misleading number.

**ROCE.** Computable but distorted. Capital employed swings from negative
(net liabilities of 15,575 at 30 Jun 2025) to positive (561,081 at 31 Dec
2025) across an unexplained equity restructuring. A return on negative
capital employed is not meaningful. Present with heavy caveating or as a
trend note rather than a headline figure.

**Annual EBITDA.** Depreciation is not disclosed for FY2024 or FY2025, so
annual EBITDA cannot be computed without assuming a depreciation figure.
Either omit annual EBITDA or derive it under a clearly logged assumption.

### Not supported, dropped from scope

**Month on month growth.** No monthly data exists in any source document.
The Company reports on a half-year and annual basis only, as required for a
Euronext Access issuer. MoM is dropped and the reason documented. Where the
assignment brief lists MoM, the report substitutes period-over-period and
half-year-on-half-year growth, which is the finest granularity the source
data supports.

**Per-customer revenue data.** Only aggregate counts and percentage splits
by channel are published. No customer-level financial records exist. This
has a direct schema consequence: the provisional Customer entity in the ER
diagram cannot be populated and should be replaced by a ChannelSegment
entity holding aggregate figures per channel per period.

**Free cash flow bridge, full form.** The components exist (operating cash
flow, capital expenditure of 8,500) but capital expenditure is minimal and
the bridge would be trivially short. Present a simplified EBITDA to
operating cash flow bridge instead.

## Data quality findings

Three issues found in the source documents during inventory. All are
recorded here and in the assumptions log, and the extraction pipeline's
validation layer should surface rather than silently absorb them.

**Finding 1: arithmetic inconsistency in the HY2025 comparative.**
DOC-02, page 5, consolidated profit and loss states turnover 340,931, cost of sales
69,600, gross profit 272,331. Turnover minus cost of sales gives 271,331,
a discrepancy of 1,000. The stated gross profit is corroborated by two
independent checks: it reconciles with the operating loss (272,331 less
administrative expenses 677,908 equals the stated 405,577), and it produces
the stated gross margin of 79.8%. Cost of sales is therefore the erroneous
line and should be 68,600. Treatment: ingest cost of sales as printed with
a validation flag, and use the stated gross profit for all derived metrics.
Do not silently correct the source.

**Finding 2: entity and reporting basis change across periods.**
FY2024 and FY2025 figures are for ADF Farm Solutions Limited on a company
basis (DOC-01 page 25; DOC-02 page 5). HY2025 and HY2026 figures are for Senus PLC on a consolidated group
basis. The entity was renamed and re-registered as a PLC on 17 Dec 2025,
and Loamin Limited was acquired on 14 Nov 2025. Annual and half-year figures
are therefore not on an identical basis and year-on-year comparison across
that boundary carries a caveat. Treatment: store reporting entity and basis
as attributes on the source document, and surface the caveat wherever
annual and half-year figures appear in the same view.

**Finding 3: unexplained equity movement.**
Between 30 Jun 2025 and 31 Dec 2025, retained earnings move from -865,681
to +236,081, share premium falls from 849,963 to 300,000, and called up
share capital rises from 144 to 25,000 (DOC-01 page 25 for the 30 Jun 2025 position; DOC-02 pages 5 to 6 for the 31 Dec 2025 position).
The half-year loss of 485,144 does
not account for a positive swing of this size in retained earnings. The
pattern is consistent with a capital reorganisation on re-registration as a
PLC, but no note in DOC-02 explains it. Treatment: flag on any equity-based
metric, particularly ROCE, and record as an open question.

**Minor.** DOC-03 title slide is dated March 2025 while the filename, footer
and content are March 2026. DOC-02 note 4 states goodwill of 669,500 while
the balance sheet states 669,550. The balance sheet figure is used.

## Consequences for the build

1. The Customer entity is replaced by ChannelSegment. Confirmed by the
   absence of any per-customer data.
2. SourceDocument needs reporting_entity and reporting_basis attributes to
   carry Finding 2.
3. FinancialLineItem needs a validation flag or status field to carry
   Finding 1 without overwriting the raw value.
4. Metric definitions must carry an availability scope, since several
   metrics exist for some periods and not others. The UI must handle absent
   periods rather than rendering gaps as zero.
5. Figures stated in prose (bookings, R&D percentages, pipeline) must be
   distinguishable from figures extracted from statements, since their
   reliability differs. This is what the confidence score is for.
