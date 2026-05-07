"""
Convert review_results/paper<N>_skill.json files to the reviews/openaireview/
JSONL format produced by save_openaireview.py.

Each input JSON has the same {"methods": {..., "comments": [...]}} shape as
the openaireview backend response, so we reuse the exact same extraction
logic (title / explanation -> "title: explanation").

Output: reviews/openaireview/<min>_<max>.jsonl, where the range covers the
paper indices found in review_results/.

Usage:
    python convert_review_results.py
"""

import json
import re
import sys
from pathlib import Path

INPUT_DIR = Path("review_results")
OUTPUT_DIR = Path("reviews/openaireview")


def extract_items(data: dict) -> list[str]:
    items = []
    for method in data.get("methods", {}).values():
        for comment in method.get("comments", []):
            if (comment.get("severity") or "").strip().lower() == "minor":
                continue
            title = comment.get("title", "").strip()
            explanation = comment.get("explanation", "").strip()
            if title and explanation:
                items.append(f"{title}: {explanation}")
            elif title:
                items.append(title)
            elif explanation:
                items.append(explanation)
    return items


def main() -> int:
    pattern = re.compile(r"^paper(\d+)_skill\.json$")
    files = []
    for f in INPUT_DIR.iterdir():
        m = pattern.match(f.name)
        if m:
            files.append((int(m.group(1)), f))

    if not files:
        print(f"ERROR: no paper<N>_skill.json files found in {INPUT_DIR}/", file=sys.stderr)
        return 1

    files.sort(key=lambda t: t[0])
    indices = [idx for idx, _ in files]
    out_path = OUTPUT_DIR / f"{indices[0]}_{indices[-1]}.jsonl"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as out:
        for idx, path in files:
            with open(path) as f:
                data = json.load(f)
            items = extract_items(data)
            record = {"paper": f"paper{idx}.pdf", "token": "", "items": items}
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"  paper{idx}.pdf -> {len(items)} comments")

    print(f"\nWrote {len(files)} record(s) to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
