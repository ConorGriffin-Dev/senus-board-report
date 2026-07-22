"""Extraction service.

Reads cached extraction outputs and validates them against the prompt's
output contract. The model call itself is the single function marked as the
swap point below.

Under project instructions section 3.1 no live API key is used. Extraction
is run manually through a chat interface with the source document attached,
and the response saved to fixtures/extraction/. This module reads those
fixtures and puts them through the same validation, confidence scoring and
source-reference handling a live response would receive.
"""

import json
from pathlib import Path

from extraction.schemas import ExtractionResult

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "extraction"
PROMPT_VERSION = "extraction_v1"

# Recorded on ExtractionRun so the provenance of each figure includes which
# model produced it. Updated by hand when a fixture is regenerated.
MODEL_NAME = "claude-opus-4-5 (via claude.ai chat interface)"


# ---------------------------------------------------------------------------
# SWAP POINT
#
# This is the only function that produces raw model output. To move from
# cached fixtures to a live Anthropic API call, replace the body of this
# function with an API request and return the response text. Nothing else in
# this module or in loader.py needs to change: validation, confidence
# scoring, source-reference handling and the database write are all
# downstream of this call and operate identically either way.
#
# A live implementation would read the prompt from prompts/extraction_v1.md,
# attach the source document, call the messages endpoint with structured
# output, and return response.content[0].text. It would also need a document
# parsing step before the call, which does not exist in this codebase under
# the fixture method. See assumption A-17.
# ---------------------------------------------------------------------------
def _fetch_extraction_output(doc_ref: str) -> str:
    """Return raw JSON text for one document's extraction.

    Currently reads a cached fixture. See the swap point note above.
    """
    fixture_path = FIXTURE_DIR / f"{doc_ref}.json"
    if not fixture_path.exists():
        raise FileNotFoundError(
            f"No extraction fixture for {doc_ref} at {fixture_path}. "
            f"Run prompts/{PROMPT_VERSION}.md against the source document "
            f"and save the response there."
        )
    return fixture_path.read_text()


def extract(doc_ref: str) -> ExtractionResult:
    """Produce a validated extraction result for one source document.

    Raises if the output does not satisfy the contract. A fixture that fails
    validation is a defect in the extraction run, and loading it partially
    would put unvalidated figures in front of a reader.
    """
    raw = _fetch_extraction_output(doc_ref)
    payload = json.loads(raw)
    return ExtractionResult.model_validate(payload)


def fixture_path_for(doc_ref: str) -> str:
    """Path recorded on ExtractionRun, relative to the repository root."""
    return f"fixtures/extraction/{doc_ref}.json"
