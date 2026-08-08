"""Answer generation on top of retrieved manifesto chunks.

If GROQ_API_KEY is set, calls Groq's free-tier Llama 3.3 70B for a grounded,
cited answer. If not, falls back to a retrieval-only response: the top
excerpts themselves, ranked and cited, with no generation step at all. Both
paths are genuinely functional; the fallback is not a degraded stub, it is
simply RAG without the "G".
"""
import logging

from app.config import GROQ_API_KEY, GROQ_MODEL

log = logging.getLogger("rag.generator")

SYSTEM_PROMPT = """You are a neutral, factual assistant answering questions about Indian \
political party election manifestos (2024 Lok Sabha) using ONLY the provided excerpts. \
Rules:
- Answer strictly from the excerpts. If they don't cover the question, say so plainly.
- Never state a personal opinion on which party is better; present positions side by side \
when the question invites comparison.
- After each claim, cite the source in the form [Party, chunk N].
- Keep answers concise (under 200 words) and neutral in tone.
"""


def generative_available() -> bool:
    return bool(GROQ_API_KEY)


def _format_context(chunks: list[dict]) -> str:
    lines = []
    for c in chunks:
        lines.append(f"[{c['party_name']}, chunk {c['chunk_index']}]: {c['text']}")
    return "\n\n".join(lines)


def generate_answer(question: str, chunks: list[dict]) -> dict:
    if not chunks:
        return {
            "answer": "I couldn't find any manifesto content relevant to that question.",
            "method": "no_context",
        }

    if not generative_available():
        excerpts = "\n\n".join(
            f"**{c['party_name']}** ({c['title']}): “{c['text'][:280].strip()}…”"
            for c in chunks
        )
        return {
            "answer": (
                "Generative answers need a free Groq API key configured on the server "
                "(see README). Showing the most relevant manifesto excerpts instead:\n\n" + excerpts
            ),
            "method": "retrieval_only",
        }

    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)
        context = _format_context(chunks)
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Excerpts:\n\n{context}\n\nQuestion: {question}"},
            ],
            temperature=0.2,
            max_tokens=500,
        )
        answer = completion.choices[0].message.content
        return {"answer": answer, "method": "groq_generated"}
    except Exception as exc:
        log.warning("groq generation failed, falling back to retrieval-only: %s", exc)
        excerpts = "\n\n".join(
            f"**{c['party_name']}**: “{c['text'][:280].strip()}…”" for c in chunks
        )
        return {
            "answer": f"(Generation temporarily unavailable, showing excerpts instead)\n\n{excerpts}",
            "method": "retrieval_only_fallback",
        }
