"""
Aggregate per-service review JSONL files into reviews/<service>/full.jsonl
and run sanity checks.

For each service, walks reviews/<service>/*.jsonl, deduplicates by paper
(keeping the record with non-empty items when possible), and writes the
result to reviews/<service>/full.jsonl.

Sanity checks (printed at the end):
  1. Every paper<N>.pdf in review_pdf_files/ is present per service.
  2. Every kept record has a non-empty "items" list.
  3. Duplicate paper records were collapsed; counts are reported.

Usage:
    python aggregate_reviews.py
"""

import json
import re
import sys
from pathlib import Path

REVIEWS_DIR = Path("reviews")
PDF_DIR = Path("review_pdf_files")
SERVICES = ["openaireview", "stanford"]
FULL_FILENAME = "full.jsonl"


def expected_papers() -> set[str]:
    pattern = re.compile(r"^paper(\d+)\.pdf$")
    return {f.name for f in PDF_DIR.iterdir() if pattern.match(f.name)}


def load_service(service: str) -> tuple[dict[str, dict], list[tuple[str, str]]]:
    """Return (best record per paper, list of (paper, source_file) duplicates dropped)."""
    service_dir = REVIEWS_DIR / service
    full_path = service_dir / FULL_FILENAME
    best: dict[str, dict] = {}
    dropped: list[tuple[str, str]] = []

    for jsonl_path in sorted(service_dir.glob("*.jsonl")):
        if jsonl_path == full_path:
            continue
        with open(jsonl_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                paper = record.get("paper")
                if not paper:
                    continue
                record["source_file"] = str(jsonl_path)

                if paper not in best:
                    best[paper] = record
                    continue

                # Duplicate: prefer the record with non-empty items.
                incumbent = best[paper]
                incumbent_has_items = bool(incumbent.get("items"))
                challenger_has_items = bool(record.get("items"))
                if challenger_has_items and not incumbent_has_items:
                    dropped.append((paper, incumbent["source_file"]))
                    best[paper] = record
                else:
                    dropped.append((paper, record["source_file"]))

    return best, dropped


def main() -> int:
    expected = expected_papers()
    if not expected:
        print(f"ERROR: no paper PDFs found under {PDF_DIR}/", file=sys.stderr)
        return 1

    issues: list[str] = []

    for service in SERVICES:
        records, dropped = load_service(service)

        missing = sorted(
            expected - set(records.keys()),
            key=lambda n: int(re.match(r"paper(\d+)\.pdf$", n).group(1)),
        )
        if missing:
            issues.append(f"[{service}] missing {len(missing)} paper(s): {', '.join(missing)}")

        empty = sorted(
            (p for p, r in records.items() if not r.get("items")),
            key=lambda n: int(re.match(r"paper(\d+)\.pdf$", n).group(1)),
        )
        if empty:
            issues.append(f"[{service}] empty items in {len(empty)} record(s): {', '.join(empty)}")

        if dropped:
            preview = ", ".join(f"{p} ({Path(s).name})" for p, s in dropped[:5])
            more = "" if len(dropped) <= 5 else f" (+{len(dropped) - 5} more)"
            issues.append(f"[{service}] dropped {len(dropped)} duplicate record(s): {preview}{more}")

        sorted_records = sorted(
            records.values(),
            key=lambda r: int(re.match(r"paper(\d+)\.pdf$", r["paper"]).group(1)),
        )

        out_path = REVIEWS_DIR / service / FULL_FILENAME
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as out:
            for record in sorted_records:
                record.pop("source_file", None)
                out.write(json.dumps(record, ensure_ascii=False) + "\n")

        print(f"[{service}] {len(sorted_records)} record(s) -> {out_path}")

    print("\n=== Sanity check ===")
    if not issues:
        print("All checks passed.")
        return 0

    for issue in issues:
        print(issue)
    return 1


if __name__ == "__main__":
    sys.exit(main())
