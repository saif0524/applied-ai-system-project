from __future__ import annotations

import logging
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

logger = logging.getLogger(__name__)

MAX_QUESTION_CHARS = 500
MIN_GROUNDEDNESS = 0.25


@dataclass
class RetrievalChunk:
    text: str
    score: float
    source: str


def chunk_text(text: str, source: str, chunk_size: int = 700, overlap: int = 120) -> list[dict]:
    """Split text into overlapping chunks for retrieval."""
    if not text.strip():
        return []

    chunks: list[dict] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append({"text": text[start:end].strip(), "source": source})
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9']+", text.lower())


def _tf(tokens: Iterable[str]) -> Counter:
    return Counter(tokens)


def _cosine_similarity(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0

    common = set(a).intersection(b)
    numerator = sum(a[t] * b[t] for t in common)
    norm_a = sum(v * v for v in a.values()) ** 0.5
    norm_b = sum(v * v for v in b.values()) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return numerator / (norm_a * norm_b)


def retrieve_relevant_chunks(question: str, chunks: list[dict], top_k: int = 3) -> list[RetrievalChunk]:
    """Simple retrieval using cosine similarity on token frequencies."""
    q_vec = _tf(_tokenize(question))
    scored: list[RetrievalChunk] = []

    for ch in chunks:
        c_vec = _tf(_tokenize(ch["text"]))
        score = _cosine_similarity(q_vec, c_vec)
        scored.append(RetrievalChunk(text=ch["text"], score=score, source=ch["source"]))

    ranked = sorted(scored, key=lambda item: item.score, reverse=True)
    return ranked[:top_k]


def validate_question(question: str) -> tuple[bool, str | None]:
    """Guardrails for incoming prompt."""
    if not question.strip():
        return False, "Please enter a question."

    if len(question) > MAX_QUESTION_CHARS:
        return False, f"Question is too long ({len(question)} chars). Limit is {MAX_QUESTION_CHARS}."

    lower = question.lower()
    blocked_patterns = [
        "ignore previous instructions",
        "reveal system prompt",
        "api key",
        "password",
    ]
    if any(p in lower for p in blocked_patterns):
        return False, "This request looks unsafe. Please ask a content-focused question about your documents."

    return True, None


def groundedness_score(answer: str, contexts: list[str]) -> float:
    """Measure how much answer language overlaps with retrieved context."""
    answer_tokens = set(_tokenize(answer))
    if not answer_tokens:
        return 0.0

    context_tokens: set[str] = set()
    for ctx in contexts:
        context_tokens.update(_tokenize(ctx))

    if not context_tokens:
        return 0.0

    overlap = answer_tokens.intersection(context_tokens)
    return len(overlap) / len(answer_tokens)


def reliability_check(answer: str, contexts: list[str]) -> tuple[bool, float]:
    score = groundedness_score(answer, contexts)
    passed = score >= MIN_GROUNDEDNESS
    logger.info("Reliability check score=%.3f passed=%s", score, passed)
    return passed, score
