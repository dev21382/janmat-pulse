import type { Topic } from "../lib/api";

export default function TopicSelector({
  topics,
  active,
  onSelect,
}: {
  topics: Topic[];
  active: string;
  onSelect: (id: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {topics.map((t) => {
        const isActive = t.id === active;
        return (
          <button
            key={t.id}
            onClick={() => onSelect(t.id)}
            className="px-3 py-1.5 rounded-full text-xs font-mono uppercase tracking-wide border transition-colors"
            style={{
              borderColor: isActive ? t.hue : "rgba(242,243,250,0.14)",
              color: isActive ? t.hue : "#9397ab",
              background: isActive ? `${t.hue}1a` : "transparent",
            }}
          >
            {t.label}
          </button>
        );
      })}
    </div>
  );
}
