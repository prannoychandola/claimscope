from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "for", "from",
    "in", "is", "it", "of", "on", "or", "that", "the", "to", "was", "were",
    "with", "this", "these", "those", "than", "into", "under", "using",
    "use", "used", "we", "our", "their", "they", "which", "while",
}


def tokenize(text: str) -> list[str]:
    return [term for term in TOKEN_RE.findall(text.lower()) if term not in STOPWORDS]


@dataclass(frozen=True)
class RetrievalHit:
    doc_id: str
    score: float
    query_term_coverage: float


class BM25Retriever:
    def __init__(self, documents: list[tuple[str, str]], k1: float = 1.5, b: float = 0.75):
        if not documents:
            raise ValueError("At least one document is required")
        self.ids = [str(doc_id) for doc_id, _ in documents]
        self.tokens = [tokenize(text) for _, text in documents]
        self.lengths = [len(tokens) for tokens in self.tokens]
        self.avg_length = sum(self.lengths) / len(self.lengths) or 1.0
        self.k1 = k1
        self.b = b
        self.term_frequencies = [Counter(tokens) for tokens in self.tokens]
        self.document_frequency: Counter[str] = Counter()
        for tokens in self.tokens:
            self.document_frequency.update(set(tokens))

    def search(self, query: str, top_k: int = 5) -> list[RetrievalHit]:
        terms = tokenize(query)
        if not terms:
            return []
        unique_terms = set(terms)
        scored: list[RetrievalHit] = []
        n_docs = len(self.ids)
        for index, frequencies in enumerate(self.term_frequencies):
            score = 0.0
            for term in terms:
                tf = frequencies.get(term, 0)
                if tf == 0:
                    continue
                df = self.document_frequency[term]
                idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
                norm = tf + self.k1 * (
                    1 - self.b + self.b * self.lengths[index] / self.avg_length
                )
                score += idf * tf * (self.k1 + 1) / norm
            if score <= 0:
                continue
            coverage = len(unique_terms.intersection(frequencies)) / max(len(unique_terms), 1)
            scored.append(RetrievalHit(self.ids[index], score, coverage))
        scored.sort(key=lambda hit: (-hit.score, hit.doc_id))
        return scored[:max(1, min(int(top_k), 100))]


class TfidfRetriever:
    def __init__(self, documents: list[tuple[str, str]]):
        if not documents:
            raise ValueError("At least one document is required")
        self.ids = [str(doc_id) for doc_id, _ in documents]
        self.tokens = [tokenize(text) for _, text in documents]
        self.document_frequency: Counter[str] = Counter()
        for tokens in self.tokens:
            self.document_frequency.update(set(tokens))
        n_docs = len(self.ids)
        self.vectors: list[dict[str, float]] = []
        self.norms: list[float] = []
        for tokens in self.tokens:
            counts = Counter(tokens)
            vector = {
                term: (1 + math.log(count)) *
                (math.log((n_docs + 1) / (self.document_frequency[term] + 1)) + 1)
                for term, count in counts.items()
            }
            self.vectors.append(vector)
            self.norms.append(math.sqrt(sum(value * value for value in vector.values())) or 1.0)

    def search(self, query: str, top_k: int = 5) -> list[RetrievalHit]:
        terms = tokenize(query)
        if not terms:
            return []
        query_counts = Counter(terms)
        n_docs = len(self.ids)
        query_vector = {
            term: (1 + math.log(count)) *
            (math.log((n_docs + 1) / (self.document_frequency.get(term, 0) + 1)) + 1)
            for term, count in query_counts.items()
        }
        query_norm = math.sqrt(sum(value * value for value in query_vector.values())) or 1.0
        unique_terms = set(terms)
        scored: list[RetrievalHit] = []
        for doc_id, vector, doc_norm in zip(self.ids, self.vectors, self.norms):
            common = unique_terms.intersection(vector)
            if not common:
                continue
            dot = sum(query_vector[term] * vector[term] for term in common)
            score = dot / (query_norm * doc_norm)
            coverage = len(common) / max(len(unique_terms), 1)
            scored.append(RetrievalHit(doc_id, score, coverage))
        scored.sort(key=lambda hit: (-hit.score, hit.doc_id))
        return scored[:max(1, min(int(top_k), 100))]
