"""
Simple in-memory RAG (Retrieval-Augmented Generation).
Teacher uploads curriculum → stored here → AI searches before answering.
"""

import re
from typing import List, Dict
from datetime import datetime

# subject_slug → list of document dicts
_store: Dict[str, List[dict]] = {}


def _chunk(text: str, size: int = 400) -> List[str]:
    text = re.sub(r'\s+', ' ', text).strip()
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) < size:
            current += " " + para
        else:
            if current:
                chunks.append(current.strip())
            current = para
    if current:
        chunks.append(current.strip())
    if not chunks:
        chunks = [text[:size]]
    return chunks


def _score(chunk: str, query: str) -> float:
    stop = {'ka','ki','ke','hai','hain','kya','the','is','in','of','and','a','an',
            'mein','se','ko','ne','or','yeh','woh'}
    chunk_l = chunk.lower()
    words = [w for w in re.findall(r'\w+', query.lower()) if w not in stop]
    if not words:
        return 0.0
    score = sum(chunk_l.count(w) * (1.1 if w in chunk_l else 0) for w in words)
    if query.lower() in chunk_l:
        score += 3.0
    return score / len(words)


def add_document(subject: str, title: str, content: str, doc_type: str = "lecture") -> dict:
    _store.setdefault(subject, [])
    chunks = _chunk(content)
    doc = {
        "id":          f"{subject}_{len(_store[subject])}_{int(datetime.now().timestamp())}",
        "title":       title,
        "doc_type":    doc_type,
        "chunks":      chunks,
        "preview":     content[:300] + "..." if len(content) > 300 else content,
        "char_count":  len(content),
        "chunk_count": len(chunks),
        "created_at":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    _store[subject].append(doc)
    return doc


def search(subject: str, query: str, top_k: int = 5) -> str:
    docs = _store.get(subject, [])
    if not docs:
        return ""

    scored = []
    for doc in docs:
        for chunk in doc["chunks"]:
            s = _score(chunk, query)
            if s > 0:
                scored.append({"text": chunk, "score": s, "title": doc["title"], "type": doc["doc_type"]})

    if not scored:
        # fallback: return first chunk of first two docs
        parts = []
        for doc in docs[:2]:
            if doc["chunks"]:
                parts.append(f"[{doc['title']}]\n{doc['chunks'][0]}")
        return "\n\n".join(parts)

    scored.sort(key=lambda x: x["score"], reverse=True)
    parts = [f"[Source: {c['title']} | Type: {c['type']}]\n{c['text']}" for c in scored[:top_k]]
    return "\n\n---\n\n".join(parts)


def list_documents(subject: str) -> List[dict]:
    return [
        {"id": d["id"], "title": d["title"], "doc_type": d["doc_type"],
         "chunk_count": d["chunk_count"], "created_at": d["created_at"]}
        for d in _store.get(subject, [])
    ]


def delete_document(subject: str, doc_id: str) -> bool:
    docs = _store.get(subject, [])
    before = len(docs)
    _store[subject] = [d for d in docs if d["id"] != doc_id]
    return len(_store[subject]) < before


def list_subjects() -> List[str]:
    return list(_store.keys())
