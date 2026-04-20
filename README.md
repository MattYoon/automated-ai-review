# automated-ai-review

Automatically submit papers for AI review and save the results.

## Requirements

```bash
pip install requests pypdf
```

## Usage

Run the submit script first, then the save script.

### Stanford (paperreview.ai)

```bash
python submit_stanford.py <start> <end> <email>
python save_stanford.py
```

### OpenAI Review (openaireview.org)

```bash
python submit_openaireview.py <start> <end> <email>
python save_openaireview.py
```

`<start>` and `<end>` are the index range of papers in `review_pdf_files/` to process. `<email>` is your email address.
