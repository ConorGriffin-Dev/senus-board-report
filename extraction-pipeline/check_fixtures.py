"""Validate every extraction fixture against the output contract.

Run as a pre-load check. Any failure names the offending item, since a
fixture that does not satisfy the contract is a defect in the extraction run
rather than something to load partially.
"""

from extraction.extraction_service import extract

DOC_REFS = ["DOC-01", "DOC-02", "DOC-03"]


def main() -> None:
    failures = 0
    for ref in DOC_REFS:
        try:
            result = extract(ref)
        except Exception as exc:
            failures += 1
            print(f"{ref}: FAILED\n  {type(exc).__name__}: {exc}\n")
            continue

        flagged = sum(1 for i in result.line_items if i.validation_status == "flagged")
        print(
            f"{ref}: {len(result.line_items)} items "
            f"({flagged} flagged), {len(result.segments)} segments, "
            f"{len(result.targets)} targets"
        )

    print(
        "\nAll fixtures valid." if not failures else f"\n{failures} fixture(s) failed."
    )


if __name__ == "__main__":
    main()
