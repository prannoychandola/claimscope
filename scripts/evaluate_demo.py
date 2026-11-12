import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import rank_evidence

examples = json.loads(
    (ROOT / "data" / "eval_queries.json").read_text(encoding="utf-8-sig")
)["examples"]

for k in (1, 3, 5):
    hits = 0
    reciprocal_ranks = []
    for example in examples:
        ranked = rank_evidence(example["claim"], top_k=k)
        ids = [item["id"] for item in ranked]
        relevant = set(example["gold_evidence_ids"])
        hits += int(bool(relevant.intersection(ids)))
        ranks = [index + 1 for index, doc_id in enumerate(ids) if doc_id in relevant]
        reciprocal_ranks.append(1 / min(ranks) if ranks else 0.0)
    recall = hits / len(examples) if examples else 0.0
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
    print(f"Recall@{k}: {recall:.3f} | MRR@{k}: {mrr:.3f} | queries: {len(examples)}")

print("These figures only check retrieval on the tiny fictional demo fixture.")
