import ReactMarkdown from "react-markdown";
import type { ChatMessage } from "../hooks/useChat";
import { strings } from "../strings";
import type { Lang } from "../types";

export default function MessageList({
  messages,
  loading,
  lang,
  onRetry,
}: {
  messages: ChatMessage[];
  loading: boolean;
  lang: Lang;
  onRetry: () => void;
}) {
  return (
    <div className="chat-thread">
      {messages.length === 0 && !loading && (
        <p className="chat-hint">{strings.chatHint[lang]}</p>
      )}
      {messages.map((m, i) => (
        <div key={i} className={`chat-msg chat-msg-${m.role}`}>
          {m.failed ? (
            <div>
              <p>{strings.chatError[lang]}</p>
              <button className="retry" onClick={onRetry}>
                {strings.retry[lang]}
              </button>
            </div>
          ) : m.role === "assistant" ? (
            <div className="markdown">
              <ReactMarkdown>{m.content}</ReactMarkdown>
              {m.sources && m.sources.length > 0 && (
                <p className="chat-sources">
                  {strings.sources[lang]}: {m.sources.join(", ")}
                </p>
              )}
            </div>
          ) : (
            <p>{m.content}</p>
          )}
        </div>
      ))}
      {loading && (
        <div className="chat-msg chat-msg-assistant typing" aria-live="polite">
          <span className="dot-typing" />
          <span className="dot-typing" />
          <span className="dot-typing" />
        </div>
      )}
    </div>
  );
}
