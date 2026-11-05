# text-preprocessing-pipeline

[![CI](https://github.com/31242526-svg/text-preprocessing-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/31242526-svg/text-preprocessing-pipeline/actions/workflows/ci.yml)

Config-driven text cleaning for research corpora: normalise, tokenise, strip stopwords,
lemmatise — with a YAML file that records exactly which choices were made.

Most preprocessing bugs in papers come from undocumented defaults. This pipeline makes
every step explicit and reproducible, and it has no NLTK downloads to break on a
locked-down lab machine.

## What it does

| Step | Default | Config key |
| --- | --- | --- |
| Unicode normalisation (NFKC) | on | always |
| strip HTML tags and entities | on | `strip_html` |
| remove URLs | on | `remove_urls` |
| lowercase | on | `lowercase` |
| regex tokenisation | on | always |
| drop tokens shorter than 2 chars | on | `min_token_length` |
| remove stopwords | on | `remove_stopwords` |
| rule-based lemmatisation | on | `lemmatize` |
| keep digits | off | `keep_numbers` |

## Quick start

```bash
pip install -e ".[dev]"
textprep examples/corpus.txt --config configs/default.yml -o tokens.jsonl
```

Each output line is one JSON object:

```json
{"line": 1, "tokens": ["study", "run", "late", "participant", "report", "worse", "sleep"]}
```

Plain text output is available too:

```bash
textprep examples/corpus.txt --format text
```

## Use it as a library

```python
from textprep import Config, preprocess

cfg = Config(remove_stopwords=True, lemmatize=True)
tokens = preprocess("<p>The studies were running&nbsp;late.</p>", cfg)
# ['study', 'run', 'late']
```

## Config file

```yaml
lowercase: true
strip_html: true
remove_urls: true
remove_stopwords: true
lemmatize: true
min_token_length: 2
keep_numbers: false
```

Unknown keys are rejected rather than silently ignored, so a typo cannot quietly
change your results.

## Limitations

- The lemmatiser is rule-based, not a full morphological analyser. It handles plurals,
  `-ing` and `-ed`, with an exception list for Greek-origin plurals such as `analysis`.
  For linguistically precise work, swap in spaCy and keep the config contract.
- Stopwords are English only.
- Language detection is out of scope; this expects one language per file.

## Tests

```bash
pytest
```

MIT licensed.
