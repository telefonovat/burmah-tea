import { useEffect, useRef, useState } from "react";
import SiteHeader from "./components/SiteHeader";

interface Message {
  role: "user" | "assistant";
  text: string;
  sources?: string[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send() {
    const content = input.trim();
    if (!content || loading) return;
    setInput("");
    const history = [...messages, { role: "user" as const, text: content }];
    setMessages(history);
    setLoading(true);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: history.map((m) => ({ role: m.role, content: m.text })),
        }),
      });
      const data = await res.json();
      setMessages((m) => [
        ...m,
        { role: "assistant", text: data.answer, sources: data.sources },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: "ချိတ်ဆက်မှု မအောင်မြင်ပါ။ Backend လည်ပတ်နေပါသလား?" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <SiteHeader />
      <div className="chat-page">
        <div className="chat-window">
        <div className="chat-toolbar">
          <button className="chat-new" onClick={() => setMessages([])}>
            ＋ New chat
          </button>
        </div>

        <div className="chat-thread">
          {messages.length === 0 && (
            <p className="chat-hint">ဒီနေ့ ဒိုင်းဂျက်အကြောင်း မေးမြန်းနိုင်ပါသည်။</p>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`chat-msg chat-msg-${m.role}`}>
              <p>{m.text}</p>
              {m.sources && m.sources.length > 0 && (
                <p className="chat-sources">Sources: {m.sources.join(", ")}</p>
              )}
            </div>
          ))}
          {loading && <div className="chat-msg chat-msg-assistant">…</div>}
          <div ref={bottomRef} />
        </div>

        <div className="chat-input-row">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            placeholder="မေးခွန်း ရေးပါ… (Shift+Enter = စာလုံးအသစ်)"
            rows={2}
          />
          <button onClick={send} disabled={loading}>
            ➤
          </button>
        </div>
      </div>
      </div>
    </>
  );
}
