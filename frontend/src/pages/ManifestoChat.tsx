import { useEffect, useRef, useState } from "react";
import { api, RagResponse, RagStatus } from "../lib/api";

type Message = { role: "user" | "assistant"; content: string; sources?: RagResponse["sources"]; method?: string };

const SUGGESTIONS = [
  "What does each party promise on unemployment?",
  "Compare the farmer/MSP promises across parties.",
  "What is proposed on women's welfare schemes?",
  "What do the manifestos say about healthcare?",
];

export default function ManifestoChat() {
  const [status, setStatus] = useState<RagStatus | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.ragStatus().then(setStatus).catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function ask(question: string) {
    if (!question.trim() || busy) return;
    setMessages((m) => [...m, { role: "user", content: question }]);
    setInput("");
    setBusy(true);
    try {
      const res = await api.ragQuery(question);
      setMessages((m) => [...m, { role: "assistant", content: res.answer, sources: res.sources, method: res.method }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", content: "Something went wrong reaching the RAG pipeline." }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <header className="space-y-3">
        <p className="text-[11px] font-mono uppercase tracking-[0.08em] text-[#56c8d0]">
          RAG over official manifestos · 2024 Lok Sabha
        </p>
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight">Manifesto Chat</h1>
        <p className="text-sm text-[#9ea3bb] max-w-2xl">
          Ask questions across the BJP, INC and CPI(M) 2024 manifestos. Answers are grounded in retrieved
          excerpts with citations — never invented.
        </p>
        {status && (
          <div className="flex flex-wrap gap-2 pt-1">
            {status.parties.map((p) => (
              <span
                key={p.party_id}
                className="text-[11px] font-mono px-2.5 py-1 rounded-full border"
                style={{
                  borderColor: `${p.hue}55`,
                  color: p.ingested ? p.hue : "#75798c",
                  background: p.ingested ? `${p.hue}12` : "transparent",
                }}
              >
                {p.ingested ? "●" : "○"} {p.party_name}
              </span>
            ))}
            {!status.generative_available && (
              <span className="text-[11px] font-mono px-2.5 py-1 rounded-full border border-white/10 text-[#9397ab]">
                Retrieval-only mode (no GROQ_API_KEY set)
              </span>
            )}
          </div>
        )}
      </header>

      <div className="glass rounded-2xl flex flex-col h-[520px]">
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.length === 0 && (
            <div className="space-y-3">
              <p className="text-sm text-[#75798c]">Try asking:</p>
              <div className="flex flex-wrap gap-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => ask(s)}
                    className="text-xs px-3 py-1.5 rounded-full border border-white/10 text-[#cfd3e5] hover:border-white/25"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
              <div
                className={`max-w-[85%] rounded-xl px-4 py-3 text-sm whitespace-pre-wrap ${
                  m.role === "user" ? "bg-white/10 text-white" : "bg-white/[0.04] border border-white/10 text-[#dfe2ee]"
                }`}
              >
                {m.content}
                {m.sources && m.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/10 space-y-2">
                    <p className="text-[10px] font-mono uppercase tracking-wide text-[#75798c]">Sources</p>
                    {m.sources.map((s, j) => (
                      <div key={j} className="text-xs text-[#9397ab]">
                        <span className="text-[#b2b6ca] font-medium">{s.party_name}</span> — {s.title}, chunk{" "}
                        {s.chunk_index}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {busy && <div className="text-xs text-[#75798c] font-mono">thinking…</div>}
          <div ref={bottomRef} />
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            ask(input);
          }}
          className="border-t border-white/10 p-3 flex gap-2"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about the manifestos…"
            className="flex-1 bg-white/5 rounded-lg px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-white/20 placeholder:text-[#75798c]"
          />
          <button
            type="submit"
            disabled={busy}
            className="px-4 py-2 rounded-lg bg-[#9184d9] text-[#0f1120] text-sm font-medium disabled:opacity-50"
          >
            Ask
          </button>
        </form>
      </div>
    </div>
  );
}
