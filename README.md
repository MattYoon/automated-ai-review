# automated-ai-review

Scripts to submit papers for AI review and retrieve the results. Papers are in `review_pdf_files/` and indexed numerically (paper1, paper2, …).

## Requirements

```bash
pip install requests pypdf
```

## Workflow

1. Create your own branch.
2. Run the **submit** script. This uploads your assigned papers and saves access tokens locally.
3. After some time (~1 hour), you will recieve emails that your submission is ready. Then run the **save** script. This uses the tokens to fetch and save the reviews.
4. Push to your branch.
5. Repeat step 2-4 every day with new paper indicies.

## Daily limits

| Platform | Papers/24h |
|---|---|
| paperreview.ai (Stanford) | 5 |
| openaireview.org | 3 |

You will be assigned a range of paper indexes. Run a batch each day until your range is done. 

## Usage

Replace `<start>` and `<end>` with some range within your assigned index range, and `<email>` with your email. 

### Stanford (paperreview.ai)

```bash
python submit_stanford.py <start> <end> <email>
python save_stanford.py access_tokens/stanford/<start>_<end>.json
```

For example,
```bash
python submit_stanford.py 1 5 youremail@email.com # saves access_tokens/stanford/1_5.json
# run below once you've received review ready email (~1 hour).
python save_stanford.py access_tokens/stanford/1_5.json # saves reviews/stanford/1_5.jsonl
```

### OpenAI Review (openaireview.org)

```bash
python submit_openaireview.py <start> <end> <email>
python save_openaireview.py access_tokens/openaireview/<start>_<end>.json
```

Tokens are written to `access_tokens/<service>/<start>_<end>.json` and reviews to `reviews/<service>/<start>_<end>.jsonl`. If the submission fails due to 429 Error (Rate limit), the `<end>` will be overrided with the last successful index.