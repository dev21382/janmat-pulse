import json
import logging

import scipy.sparse as sp

from app.config import INDEX_DIR
from app.rag.embeddings import deserialize_vectorizer, serialize_vectorizer

log = logging.getLogger("rag.index_store")

MATRIX_PATH = INDEX_DIR / "manifesto_tfidf.npz"
VECTORIZER_PATH = INDEX_DIR / "manifesto_vectorizer.pkl"
META_PATH = INDEX_DIR / "manifesto_meta.json"


def build_and_save(chunks: list[dict], vectorizer, matrix) -> None:
    sp.save_npz(MATRIX_PATH, matrix)
    VECTORIZER_PATH.write_bytes(serialize_vectorizer(vectorizer))
    META_PATH.write_text(json.dumps(chunks), encoding="utf-8")
    log.info("saved tf-idf index chunks=%d features=%d", len(chunks), matrix.shape[1])


def load_index():
    if not (MATRIX_PATH.exists() and VECTORIZER_PATH.exists() and META_PATH.exists()):
        return None, None, None
    matrix = sp.load_npz(MATRIX_PATH)
    vectorizer = deserialize_vectorizer(VECTORIZER_PATH.read_bytes())
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    return matrix, vectorizer, meta


def index_exists() -> bool:
    return MATRIX_PATH.exists() and VECTORIZER_PATH.exists() and META_PATH.exists()
