# Validation Notes: DOC-01 Extraction, prompt v1

Fixture: `fixtures/extraction/DOC-01.json`
Prompt: `prompts/extraction_v1.md` (v1)
Source: Senus PLC Information Document, Euronext Access listing, December 2025
Extraction method: manual, via Claude.ai chat interface
Validated: 2026-07-21

## Method

Full census of all 65 extracted items: 51 line items, 9 segments, 5 targets.
Each checked on four dimensions as with DOC-02: value, period attribution,
location reference, and classification.

DOC-01 differs from DOC-02 in a way that matters for validation. DOC-02 is
nine pages of financial statements where nearly every figure sits in a
labelled table. DOC-01 is forty-five pages of mostly prose, with one summary
financial table and the remaining figures scattered across narrative
sections. Roughly half the extracted line items come from prose rather than
statements, which raises both the risk of misattribution and the difficulty
of verifying location references.

## Results

| Dimension | Checked | Errors | Error rate |
|---|---|---|---|
| Value transcription | 65 | 0 | 0.0% |
| Period attribution | 65 | 3 | 4.6% |
| Page and location reference | 65 | 0 | 0.0% |
| Classification | 65 | 0 | 0.0% |
| **Overall** | **65** | **3** | **4.6%** |

Zero transcription errors. Three period attribution defects, all of the same
kind and all already self-flagged by the extraction. Discussed below.

## Defects found

### V-03: Point-in-time facts forced into a reporting period

**Items:** Private placement gross proceeds, implied share price, post money
enterprise valuation, issued share capital, employee headcount. Five items,
three of which the extraction flagged itself.

**Problem:** These are facts as at Admission on 22 December 2025. That date
falls in HY2026, not FY2025. All five are attributed to FY2025.

**Cause:** Not extraction error. `FinancialLineItem.reporting_period_id` is
`nullable=False`, so every figure must belong to a period. There is no
representation for a point-in-time fact. The extraction chose the nearest
available period and flagged the compromise on three of the five.

**Why only three were flagged:** the extraction flagged the placement,
headcount and share price but not the valuation or share capital. That is an
inconsistency in its own flagging rather than a difference in the underlying
problem. All five have the same defect.

**Severity:** Moderate. Any period-based query for FY2025 returns five
figures that do not belong to FY2025. The private placement is the most
consequential, since it also contradicts the DOC-03 record of the same event.

**Resolution:** Deferred to the loader rather than the schema. Adding a
point-in-time period entity for five items is disproportionate. The loader
should either skip these items or attribute them to HY2026, and the decision
must be recorded. See the loader design questions at the end.

## Findings confirmed

The extraction flagged six items. All six verified as correct. One further
inconsistency was found during validation that the extraction did not catch,
recorded as F-04 below.

**FY2024 loss before tax exceeds operating loss in the wrong direction.**
Operating loss 1,130,729, loss before tax 1,130,458. The loss before tax is
smaller by 271, implying net interest income. FY2025 runs the other way:
operating loss 633,694, loss before tax 635,768, a difference of 2,074
implying net interest expense. Verified as printed in both columns. The
summary table discloses no interest lines, so neither direction can be
corroborated. Correctly flagged rather than resolved.

**Debtor movement does not reconcile.** Prose states debtors reduced by
51,727 while also stating trade debtors fell from 142,361 to 66,990, a fall
of 75,371. The gap of 23,644 implies non-trade debtors rose, which is not
stated. Verified. Correctly flagged on both items.

**Implied share price precision.** 5.126 stated to three decimals against a
`numeric(18,2)` column. Verified. The flag is appropriate, though the
underlying issue is a schema limitation rather than a source problem. See
the schema question at the end.

**Private placement period attribution.** Covered under V-03.

**Employee headcount period attribution.** Covered under V-03.

### F-04: Operating loss does not reconcile with stated administrative expenses

Not flagged by the extraction. Found during validation.

For FY2025, gross profit 648,450 less administrative expenses 1,286,058
gives an operating loss of 637,608. The stated operating loss is 633,694, a
difference of 3,914. Reconciliation would require other operating income of
3,914, which is not disclosed in the summary table.

The same test on FY2024 leaves a gap of 2,353 against the implied
administrative expenses figure, which the extraction did note in passing on
the administrative expenses item.

This is the same class of problem as the debtor discrepancy: prose figures
that do not reconcile with the summary table. It should have been flagged.
The extraction checked subtotals within the summary table but did not check
prose figures against it, because prompt v1 rule 6 says to check subtotals
against their components and these are not presented as components of a
subtotal.

**Action:** The administrative expenses item should carry a flag. Prompt
guidance should be extended to require cross-checking narrative figures
against statement figures where a relationship exists, not just subtotals
against their own components.

## Reconciliations that hold

Checked and confirmed, which is what makes the exceptions above meaningful:

- Loss after tax of 590,256 equals the movement in net assets (574,681 to
  -15,575) exactly, and the movement in retained earnings (-275,425 to
  -865,681) exactly. Both years internally consistent.
- Cash flow components sum to the stated net movement in both years.
- Opening plus net movement equals closing cash in both years, and FY2024
  closing equals FY2025 opening.
- FY2025 closing cash of 140,135 equals the opening cash in DOC-02, so the
  two documents join correctly despite the entity and basis difference.
- Gross margin computed from the extracted figures gives 77.47% for FY2025
  and 62.83% for FY2024, matching the 77.5% and 62.8% stated in prose.
- Revenue growth computes to 21.6%, matching the stated figure.
- Channel percentages sum to 100 and channel customer counts sum to 138,
  matching the headline customer figure stated elsewhere in the document.
- Geographic shares sum to 100 for FY2025.

Note the tax position implied by the extracted figures: a credit of 45,512
in FY2025 and 32,363 in FY2024, consistent with R&D tax credits for a
company at this stage. Not disclosed as a line item, so not extracted.

## Judgement calls reviewed

**The FY2024 geographic figure of 5.0 is a bound, not a value.** The source
says less than 5% of revenue came from outside Ireland. Extracted as 5.0
with confidence reduced to 0.60 and noted. The alternative was omitting it,
which would leave no FY2024 geographic comparison at all. Storing an upper
bound as though it were a point estimate is a genuine compromise, and the
low confidence score is doing real work here. The corresponding Ireland
share for FY2024 was correctly not extracted, since deriving 95% from a
bound would compound the imprecision.

**FY2024 administrative expenses were not extracted.** Inferable from the
stated FY2025 figure and the stated decrease, but not printed. Correctly
omitted under the rule against inferring absent figures. Given F-04 above,
this was the right call for a second reason: the inferred figure would not
have reconciled either.

**Governance and headcount figures were extracted.** Board meetings held and
employee headcount are not financial data. Extracting them is defensible for
completeness of the period record, and both are marked `count` rather than
`eur` so they cannot be mistaken for money. They are unlikely to feature in
the board report.

**Related party transactions were extracted at item level.** Four items
covering services supplied to and received from Onagh Consulting across both
years. Small amounts, but they are disclosed transactions with a director
connection and belong in a board report context.

## Limitations

Same self-verification caveat as DOC-02: extraction and validation were
performed by the same model in the same session. F-04 was found, which is
some evidence the check has value, but a systematic misreading would likely
survive both passes.

Materially different from DOC-02: this document is mostly prose, and prose
figures carry a location reference to a section rather than a table cell.
Verifying that "Section 7.1, Balance Sheet commentary" is the right location
is a weaker check than verifying a figure sits in a named column of a named
table. Location reference accuracy for the 26 prose-derived items should be
treated as less certain than the 0% error rate suggests.

## Conclusion

Fit for use. Zero transcription errors across 65 items, and every
reconciliation available within the summary table holds.

Two issues need resolving before load:

1. **V-03**, the five point-in-time items attributed to FY2025. A loader
   decision, not a schema change.
2. **F-04**, the unflagged administrative expenses discrepancy. The fixture
   should be amended to flag it.

One issue is deferred: the `numeric(18,2)` precision loss on the share
price. Widening the column to `numeric(18,4)` would remove a silent
alteration of a raw value, which is worth doing on principle even though the
practical impact here is one figure rounding from 5.126 to 5.13.
