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
python save_stanford.py access_tokens/stanford/<start>_<end>.json
```

### OpenAI Review (openaireview.org)

```bash
python submit_openaireview.py <start> <end> <email>
python save_openaireview.py access_tokens/openaireview/<start>_<end>.json
```

Tokens are written to `access_tokens/<service>/<start>_<end>.json` and reviews to `reviews/<service>/<start>_<end>.jsonl`.

`<start>` and `<end>` are the index range of papers in `review_pdf_files/` to process. `<email>` is your email address.
