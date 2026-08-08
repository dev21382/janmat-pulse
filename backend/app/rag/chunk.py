import re


def chunk_text(text: str, party_id: str, target_words: int = 180, overlap_words: int = 30) -> list[dict]:
    """Splits manifesto text into overlapping word-count chunks, tagged with
    an approximate page-independent index for citation purposes."""
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split(" ")
    chunks = []
    step = max(target_words - overlap_words, 1)
    for i in range(0, len(words), step):
        window = words[i : i + target_words]
        if not window:
            continue
        chunk_text_str = " ".join(window)
        if len(chunk_text_str.strip()) < 40:
            continue
        chunks.append(
            {
                "party_id": party_id,
                "chunk_index": len(chunks),
                "text": chunk_text_str,
            }
        )
        if i + target_words >= len(words):
            break
    return chunks
