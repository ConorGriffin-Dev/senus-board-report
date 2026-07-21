# Extraction Prompt v1

Version: v1
Created: 2026-07-21
Applies to: DOC-01 (Information Document), DOC-02 (Half Year Results),
DOC-03 (Corporate Presentation)
Output target: `fixtures/extraction/<doc_ref>.json`
Consumed by: `extraction-pipeline/extraction/extraction_service.py`

Run this prompt manually via a chat interface with the source document
attached. Save the raw JSON response to the fixture path above without
editing it. The pipeline validates the fixture as it would a live API
response, so hand-correcting the output would defeat the validation step.

---

## Prompt

You are extracting financial data from a published company document into a
structured database. Accuracy and traceability matter more than completeness.
A missing figure is recoverable. A wrong figure presented confidently is not.

### Task

Read the attached document and extract every financial figure, segmentation
figure, and forward-looking target it contains. Return a single JSON object
matching the schema below. Return only the JSON, with no preamble, no
commentary, and no markdown code fences.

### Core rules

1. **Transcribe, do not compute.** Extract figures exactly as printed. Do not
   calculate totals, margins, growth rates, or any derived value. Derived
   values are computed downstream in SQL where the calculation is auditable.
   If a document states a derived figure (for example a gross margin
   percentage), extract it as printed and mark `data_class` as `statement` or
   `narrative` according to where it appears.

2. **Never silently correct the source.** If figures in the document are
   arithmetically inconsistent, extract the value exactly as printed, set
   `validation_status` to `flagged`, and describe the inconsistency in
   `validation_note`. Do not adjust a value to make a subtotal reconcile. The
   raw record must reflect what the document actually says.

3. **Preserve sign conventions as printed.** Some statements present losses as
   positive numbers under a label such as "operating loss". Others use
   parentheses or minus signs. Extract the number as it appears and let the
   label carry the meaning. Record the convention in `sign_convention`.

4. **Every figure needs a location.** Populate `page_number` and
   `source_location` for every item. If you cannot identify where a figure
   came from, do not extract it.

5. **Do not infer figures that are not present.** If a document does not
   disclose depreciation, do not estimate it. If a period is not covered, do
   not extrapolate. Omission is the correct behaviour.

### Confidence scoring

Score honestly. This value drives how figures are presented to the reader, so
inflated confidence is worse than low confidence.

| Range | Use when |
|---|---|
| 0.95 to 1.00 | Figure appears in a formal financial statement table, clearly labelled, unambiguous |
| 0.85 to 0.94 | Figure appears in a table but the label is ambiguous, or the period attribution required judgement |
| 0.70 to 0.84 | Figure stated in narrative prose as a definite value |
| 0.40 to 0.69 | Figure stated as an approximation, a rounded value, or with hedging language such as "approximately" or "circa" |
| Below 0.40 | Do not extract. Note it in `extraction_notes` instead |

### Data class

- `statement`: from a formal financial statement (profit and loss, balance
  sheet, cash flow statement)
- `narrative`: from prose or a commentary section, stated as a definite value
- `approximation`: stated with hedging language, or rounded to a degree that
  implies estimation

### Period attribution

Attribute every figure to exactly one period, using these labels:

| Label | Coverage |
|---|---|
| `FY2024` | 12 months to 30 June 2024 |
| `FY2025` | 12 months to 30 June 2025 |
| `HY2025` | 6 months to 31 December 2024 |
| `HY2026` | 6 months to 31 December 2025 |

Financial statements typically present two columns, a current period and a
prior-period comparative. Extract both, attributing each to its own period.
Read column headers carefully; misattributing a comparative to the wrong
period is the most consequential error you can make here.

If a figure covers a period not in the table above, set `period_label` to
`unmapped` and describe the actual period in `source_location`.

### Statement classification

Use `profit_and_loss`, `balance_sheet`, `cash_flow`, or `narrative`.

### Output schema

```json
{
  "document": {
    "doc_ref": "DOC-02",
    "filename": "exact filename as provided",
    "document_type": "half_year_results",
    "publication_date": "2026-03-19",
    "reporting_entity": "Senus PLC",
    "reporting_basis": "group",
    "page_count": 9
  },
  "line_items": [
    {
      "label": "Turnover",
      "value": 354813.00,
      "currency": "EUR",
      "period_label": "HY2026",
      "statement": "profit_and_loss",
      "data_class": "statement",
      "page_number": 5,
      "source_location": "Consolidated Profit and Loss Account, six months to 31-Dec-25 column",
      "sign_convention": "as_printed",
      "confidence": 0.99,
      "validation_status": "valid",
      "validation_note": null
    }
  ],
  "segments": [
    {
      "segment_type": "channel",
      "segment_name": "Enterprise",
      "period_label": "FY2025",
      "revenue_share_pct": 69.0,
      "revenue_value": null,
      "customer_count": 36,
      "avg_contract_value": null,
      "page_number": 12,
      "source_location": "Section 5.1.1, Senus Commercial Model and Customers",
      "confidence": 0.95
    }
  ],
  "targets": [
    {
      "target_type": "revenue_cagr",
      "target_value": 50.0,
      "unit": "percent",
      "target_period_label": "FY2030",
      "baseline_period_label": "FY2025",
      "baseline_value": 836991.00,
      "page_number": 26,
      "source_location": "Section 7.3, Key Performance Indicators",
      "confidence": 0.95
    }
  ],
  "extraction_notes": [
    "Free-text observations: figures seen but not extracted and why, ambiguities encountered, anything a reviewer should know."
  ]
}
```

### Field constraints

- `document_type`: `information_document`, `half_year_results`,
  `presentation`, `press_release`
- `reporting_entity`: `ADF Farm Solutions Limited` or `Senus PLC`
- `reporting_basis`: `company`, `group`, or `mixed`
- `statement`: `profit_and_loss`, `balance_sheet`, `cash_flow`, `narrative`
- `data_class`: `statement`, `narrative`, `approximation`
- `validation_status`: `valid` or `flagged`. Never `failed`; that status is
  set by the pipeline, not by extraction
- `sign_convention`: `as_printed` or `negated_label`. Use `negated_label`
  where a positive number represents a loss or outflow because the label
  says so
- `segment_type`: `channel`, `geography`, `product`
- `unit` on targets: `eur`, `percent`, `ratio`, `months`, `count`
- `confidence`: number between 0 and 1, three decimal places maximum
- Monetary values: plain numbers, no currency symbols, no thousand
  separators, two decimal places
- Percentages: the number only, so 69.0 not "69%"
- `label` must be unique within a document and period combination. If a
  document uses the same label twice for genuinely different things, qualify
  it, for example "Creditors due within one year" and "Creditors due after
  more than one year"

### Worked example of a flagged item

If a profit and loss statement shows turnover 340,931, cost of sales 69,600,
and gross profit 272,331, the arithmetic does not hold: 340,931 minus 69,600
is 271,331, not 272,331. Extract all three as printed and flag the one that
appears erroneous:

```json
{
  "label": "Cost of sales",
  "value": 69600.00,
  "currency": "EUR",
  "period_label": "HY2025",
  "statement": "profit_and_loss",
  "data_class": "statement",
  "page_number": 5,
  "source_location": "Consolidated Profit and Loss Account, six months to 31-Dec-24 column",
  "sign_convention": "as_printed",
  "confidence": 0.95,
  "validation_status": "flagged",
  "validation_note": "Turnover 340,931 less cost of sales 69,600 gives 271,331, but stated gross profit is 272,331, a discrepancy of 1,000. Stated gross profit reconciles with both the operating loss and the stated 79.8% margin, so cost of sales appears misstated and should be 68,600. Value extracted as printed."
}
```

Note what this does: it records the printed value, states the discrepancy,
identifies which line is likely wrong and why, and does not alter anything.

### Before returning

Check each of these:

- Every line item has a page number and a source location
- Every figure is attributed to the correct period column
- No derived or calculated values have been invented
- Subtotals that do not reconcile are flagged, not corrected
- Confidence scores reflect where each figure actually came from
- The output is valid JSON with no code fences or surrounding text
