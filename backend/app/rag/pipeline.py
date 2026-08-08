import logging

from app.rag.chunk import chunk_text
from app.rag.embeddings import fit_vectorizer
from app.rag.generator import generate_answer, generative_available
from app.rag.index_store import build_and_save, index_exists
from app.rag.ingest import available_manifesto_texts, ingest_all_manifestos
from app.rag.retriever import invalidate_cache, retrieve
from app.rag.sources import MANIFESTOS

log = logging.getLogger("rag.pipeline")


def build_index(force: bool = False) -> dict:
    if index_exists() and not force:
        return {"status": "already_built"}

    download_results = ingest_all_manifestos()
    texts = available_manifesto_texts()
    if not texts:
        log.warning("no manifesto texts available, index not built")
        return {"status": "no_sources_available", "downloads": download_results}

    all_chunks = []
    for source in texts:
        party_chunks = chunk_text(source["text"], source["party_id"])
        for c in party_chunks:
            c["party_name"] = source["party_name"]
            c["title"] = source["title"]
        all_chunks.extend(party_chunks)

    texts_to_index = [c["text"] for c in all_chunks]
    vectorizer = fit_vectorizer(texts_to_index)
    matrix = vectorizer.transform(texts_to_index)
    build_and_save(all_chunks, vectorizer, matrix)
    invalidate_cache()

    return {
        "status": "built",
        "downloads": download_results,
        "parties_indexed": [s["party_id"] for s in texts],
        "chunk_count": len(all_chunks),
    }


def index_status() -> dict:
    from app.rag.ingest import _text_path

    return {
        "index_built": index_exists(),
        "generative_available": generative_available(),
        "parties": [
            {**m, "ingested": _text_path(m["party_id"]).exists()} for m in MANIFESTOS
        ],
    }


def answer_query(question: str, top_k: int = 5) -> dict:
    chunks = retrieve(question, top_k=top_k)
    result = generate_answer(question, chunks)
    result["sources"] = [
        {
            "party_id": c["party_id"],
            "party_name": c["party_name"],
            "title": c["title"],
            "chunk_index": c["chunk_index"],
            "excerpt": c["text"][:400],
            "relevance": c["relevance"],
        }
        for c in chunks
    ]
    return result
