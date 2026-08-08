import logging

import numpy as np

from app.rag.embeddings import embed_query
from app.rag.index_store import load_index

log = logging.getLogger("rag.retriever")

_cached_index = None
_cached_meta = None


def _get_index():
    global _cached_index, _cached_meta
    if _cached_index is None:
        _cached_index, _cached_meta = load_index()
    return _cached_index, _cached_meta


def invalidate_cache():
    global _cached_index, _cached_meta
    _cached_index, _cached_meta = None, None


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    index, meta = _get_index()
    if index is None:
        return []

    q_vec = embed_query(query).astype(np.float32).reshape(1, -1)
    scores, ids = index.search(q_vec, top_k)

    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx == -1:
            continue
        chunk = dict(meta[idx])
        chunk["relevance"] = float(score)
        results.append(chunk)
    return results
