# ClaimScope

**Inspect evidence, not just citations.**

ClaimScope is a local-first prototype for finding passages that may be relevant to a scientific claim. It keeps evidence retrieval separate from deciding whether the evidence supports the claim.

## Current capabilities

- Local browser UI with a fictional demo corpus.
- BM25 lexical retrieval for interactive exploration.
- Human review controls for supports, contradicts, partial, and insufficient.
- BM25 and TF-IDF baselines for evidence-document retrieval on SciFact.
- Evaluation reports evidence Recall@k and MRR, with SHA-256 hashes of the input files.
- No API keys, paid models, remote inference, database, or persistent user claims.

The included demo papers, claims, values, and labels are fictional software fixtures. They are not scientific sources, and their evaluation scores are not empirical results.

## Run the interactive demo

Python 3.10 or newer is required. The project uses only the standard library.

    python app.py

Open http://127.0.0.1:8000. Stop with Ctrl+C. Claims and review labels are not saved. The interactive UI currently searches only the fictional six-passage corpus.

## Evaluate on SciFact

SciFact is an established scientific claim verification dataset. Its official documentation describes claims with evidence document IDs and sentence-level rationales. The evaluator here measures document retrieval only; it does not evaluate support/refute classification.

1. Download the official SciFact archive from the [AllenAI SciFact repository](https://github.com/allenai/scifact) and review its license.
2. Extract the archive beneath data/scifact. The evaluator locates corpus.jsonl and claims_dev.jsonl recursively.
3. Run the dev evaluation:

    python scripts/evaluate_scifact.py --data-dir data/scifact --split dev --output reports/scifact-dev.json

For a quick plumbing check before the full run, use:

    python scripts/evaluate_scifact.py --data-dir data/scifact --split dev --limit 20

The script compares BM25 and unigram TF-IDF over the full abstract corpus. It evaluates only claims with annotated evidence documents; claims without gold evidence are counted separately and skipped for retrieval metrics. The default split is dev. Use train only for development, and do not describe dev scores as test-set performance. The official test labels are not public.

Metrics:
- Recall@k: fraction of annotated evidence documents retrieved in the top k.
- MRR@k: reciprocal rank of the first relevant evidence document, averaged over queries.

The report records corpus/query counts and SHA-256 hashes to make runs traceable. The [SciFact dev baseline results](benchmarks/scifact-dev-2026-11-12.md) are committed with the project. On 188 evidence-bearing queries, BM25 reached 0.872 Recall@5 and 0.790 MRR@5; TF-IDF reached 0.869 and 0.734. These are retrieval-only dev results, not support/refute classification or test-set scores.

## Data licenses and attribution

The official SciFact release has separate terms for its components:

- Claims and evidence annotations in claims files: CC BY 4.0.
- Abstract corpus: Semantic Scholar S2ORC, ODC-By 1.0.
- Upstream SciFact code: Apache 2.0.

ClaimScope's code license does not replace those data terms. The archive and corpus are not bundled; data/scifact is Git-ignored. See [data/SCIFACT_DATA.md](data/SCIFACT_DATA.md) and the upstream [license](https://github.com/allenai/scifact/blob/master/LICENSE.md) before sharing any data or derived artifacts.

## Method and limits

The current retrieval baselines tokenize words and rank abstracts. BM25 uses term frequency and document length; TF-IDF uses sparse unigram vectors and cosine similarity. No stemming, neural embeddings, reranker, or entailment model is implemented yet. A retrieval score measures lexical relevance, not support.

A strong next milestone is to add a separately evaluated verifier using the annotated evidence sentences, then report per-class macro-F1, calibration/abstention behavior, and error analysis. Split by the official benchmark partition, and avoid tuning on the held-out test set.

Related work:
- [SciFact data and formats](https://github.com/allenai/scifact)
- [CLAIM-BENCH (IJCNLP 2025)](https://aclanthology.org/2025.ijcnlp-long.127/), a broader benchmark for claim extraction, evidence extraction, and claim-evidence validation.
- [SciVER (ACL 2025)](https://aclanthology.org/2025.acl-long.420/), for multimodal scientific claim verification.
- [CiteME (NeurIPS 2024)](https://proceedings.neurips.cc/paper_files/paper/2024/hash/0ef47f7b768e1a012e3d995ac8d8fac7-Abstract-Datasets_and_Benchmarks_Track.html), which studies citation attribution rather than evidence support classification.

## Developer checks

Run lightweight unit checks:

    python -m unittest discover -s tests

Run the fictional fixture evaluation:

    python scripts/evaluate_demo.py

The fixture's scores only confirm the demo evaluator plumbing; they are not project performance claims.

## Structure

    app.py                       Local interactive demo server
    retrieval.py                 BM25 and TF-IDF retrievers
    static/                      Browser interface
    data/demo_corpus.json        Fictional passages
    data/eval_queries.json       Fictional retrieval examples
    data/SCIFACT_DATA.md         Data terms and attribution notes
    scripts/evaluate_demo.py     Fictional fixture evaluation
    scripts/evaluate_scifact.py  Real benchmark retrieval evaluation
    tests/                       Retrieval baseline checks
    benchmarks/                  SciFact dev results and input hashes

## License

ClaimScope code is released under the MIT License. Dataset terms are separate; see the data attribution note.
