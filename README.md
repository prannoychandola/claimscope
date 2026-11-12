# 🔎 ClaimScope

### Local-first scientific evidence retrieval for claim review

**Inspect evidence, not just citations.**

> ClaimScope retrieves passages that may be relevant to a scientific claim and leaves support or contradiction judgments to a human reviewer. It is a research prototype, not an automatic fact-checker.

[View the GitHub repository](https://github.com/prannoychandola/claimscope) · [View benchmark report](benchmarks/scifact-dev-2026-11-12.md) · [View CI checks](https://github.com/prannoychandola/claimscope/actions)

## 📖 Overview

Scientific claims are easier to review when the sources behind them are surfaced directly. ClaimScope provides a small local web app for exploring evidence candidates, plus reproducible BM25 and TF-IDF retrieval baselines evaluated on the SciFact development split.

The interactive demo uses a fictional six-passage corpus. The SciFact evaluator is a separate command-line tool and measures evidence-document retrieval only. Neither component predicts whether evidence supports or refutes a claim.

## ✨ Features

- 🔎 Search a claim against the local demo corpus with BM25.
- 🧾 Inspect ranked passage candidates and their retrieval signals.
- 👤 Mark passages for human review as supports, contradicts, partial, or insufficient.
- 📊 Compare BM25 and unigram TF-IDF on the SciFact development split.
- 🧪 Run unit and HTTP integration checks, plus a demo-fixture evaluation.
- 🔐 Run locally without API keys, paid models, remote inference, or saved claims.
- ⚖️ Keep dataset attribution separate from the MIT license for the project code.

The demo papers, claims, values, and labels are fictional test fixtures. They are not scientific sources and their scores are not empirical research results.

## 🛠️ Technology Stack

| Area | Technology |
|---|---|
| Language | Python 3.10+ |
| Server | Python standard-library `http.server` |
| Retrieval | In-repository BM25 and unigram TF-IDF implementations |
| Interface | HTML, CSS, and vanilla JavaScript |
| Evaluation | SciFact dev split; Recall@k and MRR@k |
| Tests | Python `unittest` and GitHub Actions |

No third-party Python packages are required for the demo or checks.

## 🧭 Architecture

The local interface sends a claim to the Python server. BM25 returns candidate passages from the fictional demo corpus; a relevance score is only a retrieval signal and is not a support verdict. SciFact evaluation runs separately over its abstract corpus.

```text
Interactive demo
Browser UI → Local HTTP API → BM25 retrieval → Fictional passages → Human review

Benchmark
SciFact claims + abstracts → BM25 / TF-IDF → Ranked documents → Recall@k / MRR@k
```

## 📂 Project Structure

```text
claimscope/
├── app.py                         Local demo server and search API
├── retrieval.py                   BM25 and TF-IDF implementations
├── static/                        Browser interface
├── data/
│   ├── demo_corpus.json           Fictional passages for the demo
│   ├── eval_queries.json          Fictional evaluator examples
│   └── SCIFACT_DATA.md            Dataset terms and attribution notes
├── scripts/
│   ├── evaluate_demo.py           Demo-fixture evaluation
│   └── evaluate_scifact.py        SciFact retrieval evaluation
├── tests/                          Retrieval and HTTP checks
├── benchmarks/                     SciFact dev report and metrics
├── .github/workflows/tests.yml     Automated checks on Python 3.10, 3.12, 3.13
├── requirements.txt                No third-party dependencies
└── README.md
```

## 🚀 Run Locally

Python 3.10 or newer is required. The demo uses only the standard library.

**Windows PowerShell**

```powershell
py -3 app.py
```

**macOS / Linux**

```bash
python3 app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Stop the server with `Ctrl+C`. The demo searches only the fictional six-passage corpus. Claims and review labels are not saved.

## 🧪 Checks

Run the project tests and demo fixture evaluation from the repository root:

```bash
python -m unittest discover -s tests -v
python scripts/evaluate_demo.py
```

GitHub Actions runs both commands on Python 3.10, 3.12, and 3.13 for pushes and pull requests. [See the workflow results](https://github.com/prannoychandola/claimscope/actions).

## 📊 SciFact Benchmark

SciFact contains scientific claims paired with evidence documents and sentence-level rationales. ClaimScope's evaluator uses the official dev split, ranks abstracts from the full corpus, and reports retrieval metrics for claims with annotated evidence documents. Claims without gold evidence are counted separately and skipped for retrieval metrics.

| Method | Recall@1 | Recall@5 | Recall@10 | MRR@5 |
|---|---:|---:|---:|---:|
| BM25 | 0.712 | 0.872 | 0.931 | 0.790 |
| Unigram TF-IDF | 0.626 | 0.869 | 0.905 | 0.734 |

This run used 5,183 abstracts and 188 evidence-bearing claims. BM25 and TF-IDF were nearly tied on Recall@5; BM25 ranked the first relevant document higher on average. These are retrieval-only dev-set results, not support/refute classification, hidden test-set results, or state-of-the-art claims. The report includes input SHA-256 hashes and additional metrics in [`benchmarks/scifact-dev-2026-11-12.md`](benchmarks/scifact-dev-2026-11-12.md).

### Reproduce the benchmark

1. Download the official [AllenAI SciFact dataset](https://github.com/allenai/scifact) and review its dataset terms.
2. Extract the archive beneath `data/scifact/`. The evaluator locates `corpus.jsonl` and `claims_dev.jsonl` recursively.
3. Run the dev evaluation:

```bash
python scripts/evaluate_scifact.py --data-dir data/scifact --split dev
```

For a quick setup check, add `--limit 20`. The full evaluation uses the complete abstract corpus. Keep the downloaded dataset local; it is excluded from Git by `.gitignore`.

## ⚖️ Data and Licensing

ClaimScope's code is released under the [MIT License](LICENSE). SciFact has separate terms for its components: the claim annotations use CC BY 4.0, the abstract corpus is attributed to Semantic Scholar S2ORC under ODC-By 1.0, and upstream SciFact code uses Apache 2.0. The dataset is not bundled with this repository. Review [`data/SCIFACT_DATA.md`](data/SCIFACT_DATA.md) and the [upstream license](https://github.com/allenai/scifact/blob/master/LICENSE.md) before redistributing dataset files or derived artifacts.

## 🔬 Method and Limitations

BM25 uses term frequency and document length; TF-IDF ranks sparse unigram vectors by cosine similarity. The current implementation has no stemming, dense embeddings, reranker, or entailment model. A high retrieval score means lexical relevance, not that a passage supports a claim.

The browser UI is a local prototype. Review labels are not persisted. Benchmark scores are from the dev split and have no confidence intervals or significance tests. The official SciFact test labels are not public.

## 👨‍💻 Author

**Prannoy Chandola** · [GitHub](https://github.com/prannoychandola)

## 📜 License

MIT License for ClaimScope code. Dataset terms remain separate; see [Data and Licensing](data/SCIFACT_DATA.md).
