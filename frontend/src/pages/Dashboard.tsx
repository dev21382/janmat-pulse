import { useEffect, useState } from "react";
import FeedList from "../components/FeedList";
import SentimentChart from "../components/SentimentChart";
import TopicSelector from "../components/TopicSelector";
import { api, FeedItem, ForecastResponse, Topic } from "../lib/api";

const METHOD_LABEL: Record<string, string> = {
  lstm: "LSTM forecast",
  naive_trend: "Linear trend (warming up)",
  insufficient_data: "Collecting data…",
};

export default function Dashboard() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [activeTopic, setActiveTopic] = useState<string>("");
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.topics().then((ts) => {
      setTopics(ts);
      if (ts.length) setActiveTopic(ts[0].id);
    });
  }, []);

  useEffect(() => {
    if (!activeTopic) return;
    setLoading(true);
    Promise.all([api.forecast(activeTopic), api.feed(activeTopic)])
      .then(([f, feedRes]) => {
        setForecast(f);
        setFeed(feedRes.items);
      })
      .finally(() => setLoading(false));
  }, [activeTopic]);

  const activeMeta = topics.find((t) => t.id === activeTopic);

  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <p className="text-[11px] font-mono uppercase tracking-[0.08em] text-[#9184d9]">
          Live sentiment · Reddit + Google News, India
        </p>
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight">Public Opinion Dashboard</h1>
        <p className="text-sm text-[#9ea3bb] max-w-2xl">
          Sentiment aggregated from public Reddit discussion and Google News coverage per topic, with a
          per-topic forecast for the next 3 days trained on the real accumulated history. X/Twitter is not
          included — its API is paid-only, so it's omitted rather than faked.
        </p>
      </header>

      <TopicSelector topics={topics} active={activeTopic} onSelect={setActiveTopic} />

      <section className="glass rounded-2xl p-5">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-sm font-medium text-[#dfe2ee]">{activeMeta?.label ?? "—"} · sentiment trend</h2>
          {forecast && (
            <span className="text-[11px] font-mono uppercase tracking-wide text-[#9397ab]">
              {METHOD_LABEL[forecast.method]}
              {forecast.points_used ? ` · ${forecast.points_used}d history` : ""}
            </span>
          )}
        </div>
        {forecast && forecast.history.length > 0 ? (
          <SentimentChart data={forecast} hue={activeMeta?.hue ?? "#9184d9"} />
        ) : (
          <div className="h-64 flex items-center justify-center text-sm text-[#75798c]">
            {loading ? "Loading…" : "No history yet — check back after the first ingestion cycle."}
          </div>
        )}
      </section>

      <section className="glass rounded-2xl p-5">
        <h2 className="text-sm font-medium text-[#dfe2ee] mb-2">Live feed</h2>
        {loading ? (
          <div className="text-sm text-[#75798c] py-8 text-center">Loading…</div>
        ) : (
          <FeedList items={feed} />
        )}
      </section>
    </div>
  );
}
