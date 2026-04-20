"""
Fetch reviews from openaireview.org for each token in the given JSON file and
save the Comments as JSONL. Overall Feedback is ignored.

Each output record contains only:
  - "paper":  the filename key from the input JSON
  - "token":  the access token
  - "items":  list of comment strings ("title: explanation")

Usage:
    python save_openaireview.py access_tokens_openaireview_1_2.json
    python save_openaireview.py access_tokens_openaireview_1_2.json --delay 2.0
"""

import json
import re
import sys
import time
import argparse
from pathlib import Path

import requests

BACKEND_URL = "https://openaireview-backend-947059889174.us-central1.run.app"


def fetch_comments(token: str) -> list[str]:
    resp = requests.get(f"{BACKEND_URL}/results/{token}", timeout=30)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for method in data.get("methods", {}).values():
        for comment in method.get("comments", []):
            title = comment.get("title", "").strip()
            explanation = comment.get("explanation", "").strip()
            if title and explanation:
                items.append(f"{title}: {explanation}")
            elif title:
                items.append(title)
            elif explanation:
                items.append(explanation)

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
                items = fetch_comments(token)
                record = {"paper": paper_name, "token": token, "items": items}
                print(f"  -> {len(items)} comments")
            except Exception as e:
                print(f"  ERROR: {e}", file=sys.stderr)
                record = {"paper": paper_name, "token": token, "items": [], "error": str(e)}

            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            time.sleep(args.delay)

    print(f"\nDone. Results written to {out_path}")


if __name__ == "__main__":
    main()
