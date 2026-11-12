from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from retrieval import BM25Retriever, TfidfRetriever


def find_unique(root: Path, filename: str) -> Path:
    matches = list(root.rglob(filename))
    if len(matches) != 1:
        raise SystemExit(
            f"Expected exactly one {filename} under {root}; found {len(matches)}. "
            "Extract the official SciFact archive to the data folder."
        )
    return matches[0]


def read_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8-sig") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise SystemExit(f"Invalid JSON at {path}:{line_number}: {error}") from error
    return records


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def score_retriever(retriever, examples: list[dict], ks: list[int]) -> dict:
    metric_rows = {k: {"recall": [], "mrr": []} for k in ks}
    for example in examples:
        gold = set(example["gold_doc_ids"])
        max_k = max(ks)
        ranked = [hit.doc_id for hit in retriever.search(example["claim"], max_k)]
        for k in ks:
            top = ranked[:k]
            metric_rows[k]["recall"].append(len(gold.intersection(top)) / len(gold))
            first = next((i + 1 for i, doc_id in enumerate(top) if doc_id in gold), None)
            metric_rows[k]["mrr"].append(1 / first if first else 0.0)
    return {
        str(k): {
            "recall_at_k": sum(values["recall"]) / len(values["recall"]),
            "mrr_at_k": sum(values["mrr"]) / len(values["mrr"]),
        }
        for k, values in metric_rows.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate BM25 and TF-IDF evidence-document retrieval on SciFact dev."
    )
    parser.add_argument("--data-dir", type=Path, default=Path("data/scifact"))
    parser.add_argument("--split", choices=("dev", "train"), default="dev")
    parser.add_argument("--limit", type=int, default=None, help="Optional smoke-run query limit")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON report path")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be a positive integer")

    data_root = args.data_dir.resolve()
    corpus_path = find_unique(data_root, "corpus.jsonl")
    claims_path = find_unique(data_root, f"claims_{args.split}.jsonl")
    corpus_rows = read_jsonl(corpus_path)
    claim_rows = read_jsonl(claims_path)

    documents = []
    for row in corpus_rows:
        abstract = row.get("abstract", [])
        if isinstance(abstract, list):
            abstract_text = " ".join(str(sentence) for sentence in abstract)
        else:
            abstract_text = str(abstract)
        text = " ".join(part for part in [str(row.get("title", "")), abstract_text] if part)
        documents.append((str(row["doc_id"]), text))

    labeled = []
    skipped_without_evidence = 0
    for row in claim_rows:
        evidence = row.get("evidence") or {}
        gold_doc_ids = [str(doc_id) for doc_id, rationales in evidence.items() if rationales]
        if not gold_doc_ids:
            skipped_without_evidence += 1
            continue
        labeled.append({
            "id": row["id"],
            "claim": str(row["claim"]),
            "gold_doc_ids": gold_doc_ids,
        })
    if args.limit is not None:
        labeled = labeled[:args.limit]
    if not documents or not labeled:
        raise SystemExit("No corpus documents or evidence-bearing claims were found.")

    ks = [1, 3, 5, 10, 20]
    bm25 = BM25Retriever(documents)
    tfidf = TfidfRetriever(documents)
    report = {
        "dataset": "SciFact",
        "split": args.split,
        "corpus_documents": len(documents),
        "claims_in_split": len(claim_rows),
        "evidence_bearing_queries_evaluated": len(labeled),
        "claims_skipped_without_gold_evidence": skipped_without_evidence,
        "limited_run": args.limit is not None,
        "files": {
            "corpus.jsonl_sha256": sha256(corpus_path),
            f"claims_{args.split}.jsonl_sha256": sha256(claims_path),
        },
        "metrics": {
            "BM25": score_retriever(bm25, labeled, ks),
            "TF-IDF": score_retriever(tfidf, labeled, ks),
        },
        "metric_note": (
            "Document-level evidence retrieval on the chosen labeled split. "
            "This does not evaluate support/refute classification."
        ),
    }
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    print(rendered)


if __name__ == "__main__":
    main()
