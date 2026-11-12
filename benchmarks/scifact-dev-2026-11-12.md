# SciFact retrieval baseline — 2026-11-12

## Setup

- Split: official SciFact dev split; no training or parameter tuning was performed.
- Corpus: 5,183 abstracts.
- Claims: 300 total; 188 had annotated evidence documents and were evaluated. The other 112 contained no gold evidence mapping and were skipped for retrieval metrics.
- Methods: in-repository BM25 and unigram TF-IDF retrievers.
- Task: retrieve gold evidence documents from the full abstract corpus.
- Metrics: evidence-document Recall@k and MRR@k.
- Input file SHA-256:
  - corpus.jsonl: b8d6c89624cb2ed74dee8938effc4f5d8bd2086887880af8110d64be4ceade62
  - claims_dev.jsonl: 86f0435d08fdb65d1aa41d1472684f57e6e71930626497bdf4d7a9ec1a632217

## Results

| Method | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Recall@20 | MRR@5 | MRR@20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| BM25 | 0.712 | 0.829 | 0.872 | 0.931 | 0.943 | 0.790 | 0.800 |
| TF-IDF | 0.626 | 0.801 | 0.869 | 0.905 | 0.939 | 0.734 | 0.741 |

## Interpretation

On this dev run, Recall@5 is nearly tied: BM25 is 0.872 and TF-IDF is 0.869. BM25 has a stronger first-relevant-document rank (MRR@5 0.790 vs 0.734). This supports BM25 as the stronger of these two simple lexical baselines for early ranking on this split, while TF-IDF retrieves almost as many evidence documents by rank five.

These scores measure evidence-document retrieval only. They do not measure whether a retrieved passage supports or contradicts a claim, and they do not establish clinical or scientific verification quality. The result is from the dev split, not the hidden test set; it is a baseline, not a state-of-the-art comparison. No confidence intervals, significance test, stemming, dense retrieval, or reranking were used.

## Reproduction

From the project root, with the official dataset extracted under data/scifact:

    python scripts/evaluate_scifact.py --data-dir data/scifact/data --split dev

The evaluator prints a machine-readable JSON report. Keep the downloaded dataset local; it is Git-ignored and has separate upstream licensing terms for claim annotations and abstracts. See [SCIFACT_DATA.md](../data/SCIFACT_DATA.md).
