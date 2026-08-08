# Janmat Pulse — Public Opinion & Manifesto Intelligence

A full rebuild of the "Public Opinion Aggregator" concept from [Dev Mann's portfolio](https://dev21382.github.io/portfolio/):
live sentiment tracking on Indian political topics, a forecast trained on that real data, and a
RAG pipeline for asking questions across the 2024 Lok Sabha party manifestos.

**Live app**: deployed on Render (see repo description for the current link).

## What's actually live vs. documented as a limitation

This is a working prototype, not a demo with mocked data. Everything below is real and running;
the limitations are stated plainly rather than papered over.

| Piece | Status |
|---|---|
| Reddit ingestion | Real, via Reddit's public unauthenticated `.json` search endpoint. Some cloud networks get rate-limited/blocked by Reddit's anti-bot measures — the pipeline degrades to News-only when that happens, rather than faking posts. |
| News ingestion | Real, via Google News RSS. No API key needed. |
| X / Twitter | **Not included.** X's API is paid-only; rather than fake it, it's omitted. |
| Sentiment scoring | Real, VADER (rule-based, no external calls). |
| Forecast | A linear-trend estimate by default. The codebase also has a small PyTorch LSTM (`ENABLE_LSTM=true`) trained per-topic on the real accumulated daily sentiment history — disabled by default because torch's RSS footprint exceeds the 512MB ceiling on free-tier hosting (confirmed by an OOM kill in production). Enable it if you deploy somewhere with ~1GB+ RAM. **Forecast quality improves the longer the deployed instance runs and accrues more real days of data**, regardless of which method is active. |
| Manifesto RAG — retrieval | Real. Official BJP/INC/CPI(M) 2024 manifesto PDFs, chunked, and ranked with TF-IDF + cosine similarity (scikit-learn) — chosen over transformer embeddings for the same memory-budget reason as the forecaster. |
| Manifesto RAG — generation | Real when a free Groq API key is configured (see below); otherwise the app serves ranked, cited excerpts directly with no generation step — still fully functional, just without prose synthesis. |

## Architecture

```
frontend/   React + Vite + TypeScript + Tailwind — Dashboard + Manifesto Chat
backend/    FastAPI — ingestion, sentiment, forecast, RAG pipeline, REST API
Dockerfile  Multi-stage build: builds the frontend, serves it as static files from FastAPI
```

One container, one process, one URL — the frontend is served by the same FastAPI app as the
API, so there's nothing to configure across origins.

## Running locally

```bash
# backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# frontend (separate terminal)
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to `localhost:8000`. Open `http://localhost:5173`.

To enable the PyTorch LSTM forecaster instead of the linear-trend default (needs more RAM):

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
ENABLE_LSTM=true uvicorn app.main:app --reload --port 8000
```

## Enabling generative RAG answers

By default the manifesto chat works with zero configuration in retrieval-only mode: it returns
the most relevant manifesto excerpts, ranked and cited. To get full generated, synthesized
answers instead:

1. Get a free API key at [console.groq.com](https://console.groq.com) (no credit card required,
   14,400 requests/day on the free tier).
2. Set it as `GROQ_API_KEY` in your deployment platform's secrets (Render → Environment). Never
   commit it to git — see `.env.example`.

## Data sources

- Reddit: `r/india`, `r/IndianPolitics`, `r/IndiaSpeaks`, `r/worldnews` via public search JSON.
- News: Google News RSS, scoped per topic, India edition.
- Manifestos: official party PDFs — [BJP Sankalp Patra](https://www.bjp.org/files/2024-04/Modi-Ki-Guarantee-Sankalp-Patra-English_2.pdf),
  [INC Nyay Patra](https://manifesto.inc.in/assets/Congress-Manifesto-English-2024-Dyoxp_4E.pdf),
  [CPI(M) Manifesto](https://cpim.org/wp-content/uploads/old/documents/election_manifesto_english_april_2024.pdf).
