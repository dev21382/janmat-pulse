import type { FeedItem } from "../lib/api";

function sentimentColor(s: number) {
  if (s > 0.15) return "#79cf9a";
  if (s < -0.15) return "#e0768f";
  return "#9397ab";
}

function timeAgo(unix: number) {
  const diff = Date.now() / 1000 - unix;
  if (diff < 3600) return `${Math.max(1, Math.round(diff / 60))}m ago`;
  if (diff < 86400) return `${Math.round(diff / 3600)}h ago`;
  return `${Math.round(diff / 86400)}d ago`;
}

export default function FeedList({ items }: { items: FeedItem[] }) {
  if (!items.length) {
    return (
      <div className="text-sm text-[#75798c] py-8 text-center">
        No live items yet for this topic — the ingestion job runs on a schedule and fills in shortly after
        deployment.
      </div>
    );
  }

  return (
    <ul className="divide-y divide-white/5">
      {items.map((item, i) => (
        <li key={i} className="py-3 flex items-start gap-3">
          <span
            className="mt-1.5 w-1.5 h-1.5 rounded-full shrink-0"
            style={{ background: sentimentColor(item.sentiment) }}
          />
          <div className="min-w-0 flex-1">
            <a
              href={item.url}
              target="_blank"
              rel="noreferrer"
              className="text-sm text-[#dfe2ee] hover:text-white line-clamp-2"
            >
              {item.title}
            </a>
            <div className="mt-1 text-[11px] font-mono uppercase tracking-wide text-[#75798c] flex items-center gap-2">
              <span>{item.source}</span>
              <span>·</span>
              <span>{timeAgo(item.created_utc)}</span>
              {item.score !== null && (
                <>
                  <span>·</span>
                  <span>{item.score} pts</span>
                </>
              )}
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
