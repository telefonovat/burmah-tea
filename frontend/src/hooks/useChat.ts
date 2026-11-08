import { useState } from "react";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  failed?: boolean;
}

// Backend is stateless; the frontend owns the history and sends the last 20 messages.
const MAX_HISTORY = 20;

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  async function request(history: ChatMessage[]) {
    setLoading(true);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: history
            .slice(-MAX_HISTORY)
            .map(({ role, content }) => ({ role, content })),
        }),
      });
      const data = await res.json();
      setMessages((m) => [
        ...m,
        { role: "assistant", content: data.answer, sources: data.sources },
      ]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "", failed: true }]);
    } finally {
      setLoading(false);
    }
  }

  function send(text: string) {
    const content = text.trim();
    if (!content || loading) return;
    const history = [...messages, { role: "user" as const, content }];
    setMessages(history);
    void request(history);
  }

  function retry() {
    // Conversation preserved: drop the failed reply, re-ask the last user message.
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === "user") {
        const history = messages.slice(0, i + 1);
        setMessages(history);
        void request(history);
        return;
      }
    }
  }

  function reset() {
    setMessages([]);
  }

  return { messages, loading, send, retry, reset };
}
