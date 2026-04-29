from __future__ import annotations

from dataclasses import dataclass
import re
from collections import Counter
from pathlib import Path


@dataclass
class KnowledgeChunk:
    text: str
    source: str
    score: float = 0.0


KNOWLEDGE_BASE = [
    {
        "source": "General Care Guide",
        "text": "Dogs generally benefit from daily exercise, mental enrichment, and consistent feeding schedules.",
    },
    {
        "source": "Medication Safety",
        "text": "Medication tasks should be treated as required and tied to feeding time when instructions require food.",
    },
    {
        "source": "Cat Care Basics",
        "text": "Cats need litter maintenance, hydration checks, and short play sessions spread across the day.",
    },
    {
        "source": "Senior Pet Notes",
        "text": "Senior pets may need shorter, more frequent walks and closer monitoring for fatigue.",
    },
    {
        "source": "Routine Reliability",
        "text": "A routine is more sustainable when high-priority and required tasks are done first within available time.",
    },
]

KB_PATH = Path("assets/knowledge_base/pet_care_kb.txt")


def _load_kb_from_txt(path: Path) -> list[dict]:
    """Load KB chunks from a lightweight tagged text file."""
    if not path.exists():
        return KNOWLEDGE_BASE

    chunks: list[dict] = []
    current_source = "Custom Knowledge"
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer, current_source
        text = " ".join(line.strip() for line in buffer if line.strip()).strip()
        if text:
            chunks.append({"source": current_source, "text": text})
        buffer = []

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.startswith("[") and line.endswith("]") and len(line) > 2:
            flush()
            current_source = line[1:-1].strip()
            continue
        buffer.append(line)

    flush()
    return chunks if chunks else KNOWLEDGE_BASE


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9']+", text.lower())


def _tf(tokens: list[str]) -> Counter:
    return Counter(tokens)


def _cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    common = set(a).intersection(b)
    num = sum(a[t] * b[t] for t in common)
    den_a = sum(v * v for v in a.values()) ** 0.5
    den_b = sum(v * v for v in b.values()) ** 0.5
    if den_a == 0 or den_b == 0:
        return 0.0
    return num / (den_a * den_b)


def retrieve_pet_knowledge(query: str, top_k: int = 2) -> list[KnowledgeChunk]:
    knowledge_base = _load_kb_from_txt(KB_PATH)
    q_vec = _tf(_tokenize(query))
    ranked: list[KnowledgeChunk] = []
    for item in knowledge_base:
        score = _cosine(q_vec, _tf(_tokenize(item["text"])))
        ranked.append(KnowledgeChunk(text=item["text"], source=item["source"], score=score))
    ranked.sort(key=lambda x: x.score, reverse=True)
    return ranked[:top_k]


def build_rag_guidance(query: str, retrieved: list[KnowledgeChunk]) -> str:
    if not retrieved:
        return "No supporting knowledge was retrieved."

    evidence = "; ".join([f"{r.source}: {r.text}" for r in retrieved])
    return (
        "Evidence-grounded guidance: prioritize required tasks first, then fit high-priority care within the time budget. "
        f"For this plan, relevant references are: {evidence}"
    )
