# automated-ai-review

Scripts to submit papers for AI review and retrieve the results. Papers are in `review_pdf_files/` and indexed numerically (paper1, paper2, …).

## Requirements

```bash
pip install requests pypdf
```

## Workflow

1. Run the **submit** script --> uploads your assigned papers and saves access tokens locally.
2. After some time (~1 hour), you will recieve emails that your submission is ready. Then run the **save** script --> uses the tokens to fetch and save the reviews.

## Daily limits

| Platform | Papers/day |
|---|---|
| paperreview.ai (Stanford) | 5 |
| openaireview.org | 3 |

You will be assigned a range of paper indexes. Run a batch each day until your range is done. Using a VPN or a different machine may let you run more in a day, but results vary.

## Usage

Replace `<start>` and `<end>` with some range within your assigned index range, and `<email>` with your email. 

### Stanford (paperreview.ai)

```bash
python submit_stanford.py <start> <end> <email>
python save_stanford.py <token_json_path>
```

For example, the existing files in this repo were generated with:

```bash
python submit_stanford.py 1 5 <email>
python save_stanford.py access_tokens_stanford_1_5.json
```

### OpenAI Review (openaireview.org)

```bash
python submit_openaireview.py <start> <end> <email>
python save_openaireview.py <token_json_path>
```

For example, the existing files in this repo were generated with:

```bash
python submit_openaireview.py 1 2 <email>
python save_openaireview.py access_tokens_openaireview_1_2.json
```

## Output files

- `access_tokens_<platform>_<start>_<end>.json` — tokens saved after submit
- `reviews_<platform>_<start>_<end>.jsonl` — reviews saved after save, if the submit script was termitated early due to too many requests (429 error), the `<end>` in the save name will be updated with the last successful one.
