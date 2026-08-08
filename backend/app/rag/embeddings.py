"""TF-IDF based text vectorization for the manifesto RAG pipeline.

Deliberately avoids sentence-transformers/torch: a transformer embedding
model plus its runtime pushes RSS well past the 512MB ceiling on free-tier
hosting (confirmed by an OOM kill in production). TF-IDF + cosine similarity
is a classic, genuinely functional retrieval method — less semantically
nuanced than dense embeddings, but it fits comfortably in memory and needs
no model download.
"""
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer

_vectorizer: TfidfVectorizer | None = None


def fit_vectorizer(texts: list[str]) -> TfidfVectorizer:
    global _vectorizer
    _vectorizer = TfidfVectorizer(stop_words="english", max_features=20000, ngram_range=(1, 2))
    _vectorizer.fit(texts)
    return _vectorizer


def get_vectorizer() -> TfidfVectorizer | None:
    return _vectorizer


def set_vectorizer(vectorizer: TfidfVectorizer) -> None:
    global _vectorizer
    _vectorizer = vectorizer


def serialize_vectorizer(vectorizer: TfidfVectorizer) -> bytes:
    return pickle.dumps(vectorizer)


def deserialize_vectorizer(data: bytes) -> TfidfVectorizer:
    return pickle.loads(data)
