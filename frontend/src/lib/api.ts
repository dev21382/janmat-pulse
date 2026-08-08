export type Topic = {
  id: string;
  label: string;
  query: string;
  hue: string;
};

export type FeedItem = {
  source: "reddit" | "news";
  title: string;
  url: string;
  created_utc: number;
  score: number | null;
  sentiment: number;
};

export type ForecastPoint = { day: string; predicted_sentiment: number };
export type HistoryPoint = { day: string; mean_sentiment: number; item_count: number };

export type ForecastResponse = {
  topic_id: string;
  method: "lstm" | "naive_trend" | "insufficient_data";
  points_used?: number;
  history: HistoryPoint[];
  forecast: ForecastPoint[];
};

export type RagSource = {
  party_id: string;
  party_name: string;
  title: string;
  chunk_index: number;
  excerpt: string;
  relevance: number;
};

export type RagResponse = {
  answer: string;
  method: string;
  sources: RagSource[];
};

export type RagStatus = {
  index_built: boolean;
  generative_available: boolean;
  parties: { party_id: string; party_name: string; title: string; url: string; hue: string; ingested: boolean }[];
};

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export const api = {
  topics: () => fetch("/api/topics").then((r) => json<Topic[]>(r)),
  feed: (topicId: string) => fetch(`/api/feed/${topicId}`).then((r) => json<{ topic_id: string; items: FeedItem[] }>(r)),
  forecast: (topicId: string) => fetch(`/api/forecast/${topicId}`).then((r) => json<ForecastResponse>(r)),
  ragStatus: () => fetch("/api/rag/status").then((r) => json<RagStatus>(r)),
  ragQuery: (question: string) =>
    fetch("/api/rag/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    }).then((r) => json<RagResponse>(r)),
};
