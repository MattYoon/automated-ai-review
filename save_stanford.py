"""
Fetch reviews from paperreview.ai for each token in the given JSON file and
save the Weaknesses section as JSONL.

Each output record contains only:
  - "paper":  the filename key from the input JSON
  - "token":  the access token
  - "items":  list of weakness bullet-point strings

Usage:
    python save_stanford.py access_tokens_stanford_1_5.json
    python save_stanford.py access_tokens_stanford_1_5.json --delay 2.0
"""

import json
import re
import sys
import time
import argparse
from pathlib import Path

import requests

BASE_URL = "https://paperreview.ai"


def fetch_weaknesses(token: str) -> list[str]:
    resp = requests.get(f"{BASE_URL}/api/review/{token}", timeout=30)
    resp.raise_for_status()
    data = resp.json()

    weaknesses_md = (data.get("sections") or {}).get("weaknesses", "")
    if not weaknesses_md:
        return []

    # Parse only indented bullet lines (sub-items); top-level bullets are category headers
    items = []
    for line in weaknesses_md.splitlines():
        if re.match(r"^\s+[-*]\s+", line):
            items.append(re.sub(r"^\s+[-*]\s+", "", line))

    return items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json", help="Path to the access tokens JSON file")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Seconds to wait between requests (default: 1.0)")
    args = parser.parse_args()

    tokens_path = Path(args.input_json)
    if not tokens_path.exists():
        print(f"ERROR: {tokens_path} not found", file=sys.stderr)
        sys.exit(1)

    stem = re.sub(r"^access_tokens_", "reviews_", tokens_path.stem)
    out_path = tokens_path.with_name(stem + ".jsonl")

    with open(tokens_path) as f:
        token_map = json.load(f)

    with open(out_path, "w", encoding="utf-8") as out_f:
        for paper_name, token in token_map.items():
            print(f"Fetching {paper_name} (token: {token[:8]}...)...")
            try:
                items = fetch_weaknesses(token)
                record = {"paper": paper_name, "token": token, "items": items}
                print(f"  -> {len(items)} weakness items")
            except Exception as e:
                print(f"  ERROR: {e}", file=sys.stderr)
                record = {"paper": paper_name, "token": token, "items": [], "error": str(e)}

            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            time.sleep(args.delay)

    print(f"\nDone. Results written to {out_path}")


if __name__ == "__main__":
    main()
