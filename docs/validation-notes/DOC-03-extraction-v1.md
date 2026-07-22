# Validation Notes: DOC-03 Extraction, prompt v1

Fixture: `fixtures/extraction/DOC-03.json`
Prompt: `prompts/extraction_v1.md` (v1)
Source: Senus short corporate presentation, March 2026
Extraction method: manual, via Claude.ai chat interface
Validated: 2026-07-21

## Method

Full census of all 13 extracted items: 4 line items, 4 segments, 5 targets.

This document is a marketing presentation with no financial statements, so
validation is mostly a question of what was correctly left out rather than
what was taken in.

## Results

| Dimension | Checked | Errors | Error rate |
|---|---|---|---|
| Value transcription | 13 | 0 | 0.0% |
| Period attribution | 13 | 0 | 0.0% |
| Page and location reference | 13 | 0 | 0.0% |
| Classification | 13 | 0 | 0.0% |
| **Overall** | **13** | **0** | **0.0%** |

No defects. All figures verified against the source and all corroborating
figures agree with their DOC-01 counterparts exactly.

## Corroboration achieved

The value of this fixture is confirmation of figures sourced elsewhere. All
of the following match DOC-01 without variation:

- Enterprise customer count of 36 for FY2025
- Geographic split of 78% Ireland and 22% outside Ireland for FY2025
- Average contract value of 12,309 for SOIL and 58,900 for ERA
- All five Senus 2030 targets: 50% revenue CAGR, 100 enterprise customers,
  50,000 average contract value, Ireland below 50% of revenue, EBITDA
  positive during FY2028

Independent agreement across two documents published three months apart
raises confidence in these figures beyond what either source gives alone.

## Unique contribution

One figure appears here with a value and in no other source: the 2023
fundraise of 800,000. DOC-01 mentions a private investment round in its
corporate history section with the same figure, so it is corroborated, but
this presentation states it in the timeline directly.

It falls in FY2023, for which no reporting period exists in this project.
Correctly recorded with `period_label` of `unmapped` rather than being
pushed into an adjacent period. The loader will need to handle unmapped
items, and skipping with a logged reason is the appropriate treatment.

## Contradiction found

The private placement is attributed to HY2026 in this fixture and to FY2025
in DOC-01, for the same event.

HY2026 is correct. The placement completed in December 2025, which falls in
the six months to 31 December 2025.

DOC-01's attribution is understandable but wrong: that document was
published on 17 December 2025 and presents the placement as a completed
current event, so the extraction attributed it to the document's own
financial year context. The extraction flagged this on the DOC-01 side.

This is the first case of two fixtures disagreeing about the same fact. It
needs an explicit precedence rule in the loader rather than last-write-wins.

## What was correctly left out

More consequential than what was taken in.

**Customer identities.** Page 5 names sixteen customers by logo: Arla, Bank
of Ireland, Tirlan, Diageo, Lakeland Dairies, Carbery, Carbon AMS, ESA,
First Milk, Farming Connect, Grennan, ABP, Department of Agriculture Food
and the Marine, SRUC, Aurivo and EIT Food. None carries a financial value.
Correctly not extracted, and correctly reasoned: the Customer entity was
removed from the schema precisely because no per-customer financial data
exists anywhere in the sources. Extracting names without values would have
recreated the entity we deliberately dropped.

**Third party market statistics.** CSRD applying to 50,000 or more
companies, and similar regulatory and market sizing claims on the Growth
Drivers slide. These describe the industry, not Senus. Correctly excluded.

**Qualitative claims.** Faster development, better market offering, wider
market reach and similar. No figures attached.

## Judgement call reviewed

**The 10x affordability claim was extracted at confidence 0.45.** The slide
states measurement at scale can be 10x more affordable using Senus and
Loamin technology combined. No baseline, no methodology, no definition of
what is being measured.

The extraction stored it as a `ratio` with a note stating it must not be
used in any computed metric.

This is arguably the wrong call. The alternative was omitting it entirely
and recording the reason in extraction notes, which is what the prompt
prescribes for anything below 0.40 confidence. At 0.45 it sits just above
that line. Storing an unfalsifiable marketing claim in a table of financial
line items, even flagged, creates a small risk that something downstream
picks it up.

The mitigation is real: `data_class` is `approximation`, confidence is low,
and the note is explicit. It stands, but the prompt should probably raise
the exclusion threshold for claims that carry no defined basis regardless of
how confidently they are stated.

## Source error noted

The title slide is dated March 2025 while the filename, page footers and all
content are March 2026. A typographical error in the source. Publication
date recorded as 2026-03-19 from the filename and footers, which agree with
the half-year results published the same day.

## Conclusion

Fit for use with no defects. Its main function is corroboration, and every
corroborating figure agrees exactly with DOC-01.

Two loader problems surfaced, neither a defect in this fixture:

1. The targets and segments here duplicate DOC-01 and will collide on the
   uniqueness constraints, which do not include the source document.
2. The private placement contradicts DOC-01 on period attribution and needs
   an explicit precedence rule.
