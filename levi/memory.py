"""
Episodic memory store.

V0 rule: vectorless. Retrieval here is exact/structured (tags, task
substring, outcome, recency) — not similarity search. This is intentional:
we want to find out how far structured retrieval gets us before reaching
for embeddings (see project notes, Section 8/9).

Storage: append-only JSONL file. Simple, inspectable, greppable.
Swap this for a real DB later without changing the interface.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .schema import EpisodicRecord, Outcome


class EpisodicMemory:
    def __init__(self, path: str = "episodic_memory.jsonl"):
        self.path = Path(path)
        self.path.touch(exist_ok=True)

    def write(self, record: EpisodicRecord) -> None:
        with self.path.open("a") as f:
            f.write(json.dumps(record.to_dict()) + "\n")

    def all(self) -> list[EpisodicRecord]:
        records = []
        with self.path.open("r") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(EpisodicRecord.from_dict(json.loads(line)))
        return records

    # --- structured retrieval (no embeddings) ---

    def by_outcome(self, outcome: Outcome) -> list[EpisodicRecord]:
        return [r for r in self.all() if r.outcome == outcome]

    def by_tag(self, tag: str) -> list[EpisodicRecord]:
        return [r for r in self.all() if tag in r.tags]

    def search_task(self, substring: str) -> list[EpisodicRecord]:
        substring = substring.lower()
        return [r for r in self.all() if substring in r.task.lower()]

    def recent(self, n: int = 5) -> list[EpisodicRecord]:
        return sorted(self.all(), key=lambda r: r.timestamp, reverse=True)[:n]

    def _tokenize(self, text: str) -> set[str]:
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = set(text.split())
        stopwords = {"a", "an", "the", "and", "or", "but", "if", "then", "else", "when", 
                     "up", "down", "left", "right", "in", "out", "on", "off", "over", "under", 
                     "again", "further", "then", "once", "here", "there", "when", "where", "why", 
                     "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", 
                     "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", 
                     "s", "t", "can", "will", "just", "don", "should", "now", "my", "i", "you", "me", "to", "is", "for", "with", "do"}
        return tokens - stopwords

    def retrieve(self, query: str, k: int = 5, threshold: float = 2.0) -> list[EpisodicRecord]:
        query_tokens = self._tokenize(query)
        query_lower = query.lower()
        
        scored_records = []
        for r in self.all():
            score = 0.0
            
            # Exact tag match: +3 per matching tag
            for tag in r.tags:
                if tag.lower() in query_tokens or tag.lower() in query_lower:
                    score += 3.0
                    
            # Task token match: +1 per overlapping token
            task_tokens = self._tokenize(r.task)
            overlap = query_tokens.intersection(task_tokens)
            score += len(overlap) * 1.0
            
            # Exact task phrase match: +2
            if query_lower in r.task.lower() or r.task.lower() in query_lower:
                score += 2.0
                
            # Outcome success bonus: +1
            if r.outcome.value == "success":
                score += 1.0
                
            if score >= threshold:
                scored_records.append((score, r))
                
        # Sort by score descending, then by timestamp descending
        scored_records.sort(key=lambda x: (x[0], x[1].timestamp), reverse=True)
        return [r for score, r in scored_records[:k]]

    def stats(self) -> dict:
        records = self.all()
        if not records:
            return {"total": 0}
        outcomes = {}
        for r in records:
            outcomes[r.outcome.value] = outcomes.get(r.outcome.value, 0) + 1
        return {"total": len(records), "by_outcome": outcomes}