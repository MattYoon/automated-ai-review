"""
Submit PDFs from review_pdf_files/ to paperreview.ai and save access tokens.

Usage:
  python submit_stanford.py                        # all files
  python submit_stanford.py <start> <end>          # 1-based inclusive range
  python submit_stanford.py <start> <end> <email>

Flow per paper:
  1. POST /api/get-upload-url  -> presigned S3 URL + s3_key
  2. POST <presigned_url>      -> upload PDF bytes directly to S3
  3. POST /api/confirm-upload  -> confirm upload, returns token
"""

import json
import os
import re
import sys

import requests
import time

BASE_URL = "https://paperreview.ai"
PDF_DIR = "review_pdf_files"


def _natural_key(name: str):
    return [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", name)]


def get_pdf_files() -> list[str]:
    files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
    files.sort(key=_natural_key)
    return [os.path.join(PDF_DIR, f) for f in files]


def submit_paper(pdf_path: str, email: str, venue: str = "") -> str:
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    filename = os.path.basename(pdf_path)

    payload = {"filename": filename}
    if venue:
        payload["venue"] = venue
    resp = requests.post(f"{BASE_URL}/api/get-upload-url", json=payload)
    resp.raise_for_status()
    data = resp.json()
    presigned_url = data["presigned_url"]
    presigned_fields = data["presigned_fields"]
    s3_key = data["s3_key"]

    form_data = {k: (None, v) for k, v in presigned_fields.items()}
    form_data["file"] = (filename, pdf_bytes, "application/pdf")
    put_resp = requests.post(presigned_url, files=form_data)
    put_resp.raise_for_status()

    confirm_resp = requests.post(
        f"{BASE_URL}/api/confirm-upload",
        data={"s3_key": s3_key, "email": email, "venue": venue or None},
    )
    confirm_resp.raise_for_status()
    return confirm_resp.json()["token"]


def load_tokens(tokens_file: str) -> dict:
    if os.path.exists(tokens_file):
        with open(tokens_file) as f:
            return json.load(f)
    return {}


def save_tokens(tokens: dict, tokens_file: str):
    with open(tokens_file, "w") as f:
        json.dump(tokens, f, indent=2)


if __name__ == "__main__":
    args = sys.argv[1:]

    start_idx = int(args[0]) if len(args) >= 1 else None
    end_idx = int(args[1]) if len(args) >= 2 else None
    user_email = args[2] if len(args) >= 3 else "dkyoon@kaist.ac.kr"

    all_pdfs = get_pdf_files()

    if start_idx is not None and end_idx is not None:
        selected = all_pdfs[start_idx - 1 : end_idx]
        tokens_file = f"access_tokens_stanford_{start_idx}_{end_idx}.json"
    else:
        selected = all_pdfs
        tokens_file = "access_tokens_stanford_all.json"

    print(f"Submitting {len(selected)} paper(s)...")

    base_start = start_idx if start_idx is not None else 1
    last_successful_idx = None

    tokens = load_tokens(tokens_file)
    for i, pdf_path in enumerate(selected):
        filename = os.path.basename(pdf_path)
        # sleep 5 seconds between submissions to avoid overwhelming the server
        time.sleep(5)
        try:
            token = submit_paper(pdf_path, user_email)
            tokens[filename] = token
            save_tokens(tokens, tokens_file)
            last_successful_idx = base_start + i
            print(f"[OK] {filename}: {token}")
            print(f"     {BASE_URL}/review?token={token}")
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                print(f"[429] Rate limited on {filename}. Stopping.")
                if last_successful_idx is not None:
                    new_tokens_file = f"access_tokens_stanford_{base_start}_{last_successful_idx}.json"
                    os.rename(tokens_file, new_tokens_file)
                    print(f"Tokens saved to {new_tokens_file}")
                else:
                    print("No successful submissions; no token file saved.")
                sys.exit(1)
            print(f"[FAIL] {filename}: {e}")

    print(f"\nTokens saved to {tokens_file}")
