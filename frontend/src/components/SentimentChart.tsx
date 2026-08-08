import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ForecastResponse } from "../lib/api";

export default function SentimentChart({ data, hue }: { data: ForecastResponse; hue: string }) {
  const lastHistoryDay = data.history.at(-1)?.day;

  const merged = [
    ...data.history.map((h) => ({ day: h.day, historical: h.mean_sentiment, forecast: null as number | null })),
    ...data.forecast.map((f, i) => ({
      day: f.day,
      historical: null as number | null,
      forecast: f.predicted_sentiment,
      bridge: i === 0 ? data.history.at(-1)?.mean_sentiment : undefined,
    })),
  ];

  // bridge the gap so the dashed forecast line visually connects to the solid one
  if (merged.length && data.forecast.length && data.history.length) {
    const bridgeIdx = data.history.length - 1;
    (merged[bridgeIdx] as any).forecast = data.history.at(-1)?.mean_sentiment;
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={merged} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(242,243,250,0.08)" />
          <XAxis dataKey="day" tick={{ fill: "#9397ab", fontSize: 11 }} tickLine={false} axisLine={{ stroke: "rgba(242,243,250,0.1)" }} />
          <YAxis
            domain={[-1, 1]}
            tick={{ fill: "#9397ab", fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: "rgba(242,243,250,0.1)" }}
          />
          <ReferenceLine y={0} stroke="rgba(242,243,250,0.15)" />
          {lastHistoryDay && (
            <ReferenceLine x={lastHistoryDay} stroke="rgba(242,243,250,0.2)" strokeDasharray="2 2" />
          )}
          <Tooltip
            contentStyle={{ background: "#12141f", border: "1px solid rgba(242,243,250,0.1)", borderRadius: 8 }}
            labelStyle={{ color: "#f2f3fa" }}
          />
          <Legend wrapperStyle={{ fontSize: 12, color: "#9397ab" }} />
          <Line type="monotone" dataKey="historical" name="Observed" stroke={hue} strokeWidth={2} dot={false} connectNulls />
          <Line
            type="monotone"
            dataKey="forecast"
            name="Forecast"
            stroke={hue}
            strokeWidth={2}
            strokeDasharray="5 4"
            dot={{ r: 3 }}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
