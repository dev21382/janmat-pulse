import logging

log = logging.getLogger("rag.embeddings")

_model = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        from app.config import EMBEDDING_MODEL

        log.info("loading embedding model %s", EMBEDDING_MODEL)
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]):
    model = get_model()
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=False)


def embed_query(text: str):
    model = get_model()
    return model.encode([text], normalize_embeddings=True, show_progress_bar=False)[0]
