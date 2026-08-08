import json
import logging

import numpy as np

from app.config import INDEX_DIR

log = logging.getLogger("rag.index_store")

INDEX_PATH = INDEX_DIR / "manifesto.faiss"
META_PATH = INDEX_DIR / "manifesto_meta.json"


def build_and_save(chunks: list[dict], vectors: np.ndarray) -> None:
    import faiss

    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity via normalized inner product
    index.add(vectors.astype(np.float32))
    faiss.write_index(index, str(INDEX_PATH))
    META_PATH.write_text(json.dumps(chunks), encoding="utf-8")
    log.info("saved faiss index chunks=%d dim=%d", len(chunks), dim)


def load_index():
    import faiss

    if not INDEX_PATH.exists() or not META_PATH.exists():
        return None, None
    index = faiss.read_index(str(INDEX_PATH))
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    return index, meta


def index_exists() -> bool:
    return INDEX_PATH.exists() and META_PATH.exists()
