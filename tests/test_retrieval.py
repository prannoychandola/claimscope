import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import rank_evidence
from retrieval import BM25Retriever, TfidfRetriever


class RetrievalBaselineTests(unittest.TestCase):
    def test_known_demo_claim_retrieves_its_gold_passage_first(self):
        claim = "Hybrid retrieval achieved recall at five of 0.82 while BM25 scored 0.75."
        results = rank_evidence(claim, top_k=3)
        self.assertTrue(results)
        self.assertEqual(results[0]["id"], "DEMO-001")

    def test_bm25_and_tfidf_rank_relevant_document_first(self):
        documents = [
            ("a", "hybrid retrieval improves evidence recall"),
            ("b", "weather patterns affect seasonal rainfall"),
            ("c", "retrieval systems rank evidence passages"),
        ]
        for retriever in (BM25Retriever(documents), TfidfRetriever(documents)):
            results = retriever.search("hybrid retrieval evidence recall", top_k=2)
            self.assertTrue(results)
            self.assertEqual(results[0].doc_id, "a")

    def test_stopword_only_claim_has_no_candidates(self):
        docs = [("a", "evidence retrieval"), ("b", "paper claims")]
        for retriever in (BM25Retriever(docs), TfidfRetriever(docs)):
            self.assertEqual(retriever.search("and the to", top_k=5), [])

    def test_top_k_is_capped(self):
        docs = [(str(i), "retrieval evidence " + str(i)) for i in range(112)]
        self.assertLessEqual(len(BM25Retriever(docs).search("retrieval", top_k=1000)), 100)
        self.assertLessEqual(len(TfidfRetriever(docs).search("retrieval", top_k=1000)), 100)


if __name__ == "__main__":
    unittest.main()

