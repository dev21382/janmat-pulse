import logging

from sklearn.metrics.pairwise import cosine_similarity

from app.rag.index_store import load_index

log = logging.getLogger("rag.retriever")

_cached_matrix = None
_cached_vectorizer = None
_cached_meta = None


def _get_index():
    global _cached_matrix, _cached_vectorizer, _cached_meta
    if _cached_matrix is None:
        _cached_matrix, _cached_vectorizer, _cached_meta = load_index()
    return _cached_matrix, _cached_vectorizer, _cached_meta


def invalidate_cache():
    global _cached_matrix, _cached_vectorizer, _cached_meta
    _cached_matrix, _cached_vectorizer, _cached_meta = None, None, None


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    matrix, vectorizer, meta = _get_index()
    if matrix is None:
        return []

    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, matrix)[0]
    ranked = scores.argsort()[::-1][:top_k]

    results = []
    for idx in ranked:
        if scores[idx] <= 0:
            continue
        chunk = dict(meta[idx])
        chunk["relevance"] = float(scores[idx])
        results.append(chunk)
    return results
