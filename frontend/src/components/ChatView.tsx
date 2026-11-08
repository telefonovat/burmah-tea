import { useChat } from "../hooks/useChat";
import { strings } from "../strings";
import type { Lang } from "../types";
import ChatInput from "./ChatInput";
import MessageList from "./MessageList";
import PromptChips from "./PromptChips";

export default function ChatView({ lang }: { lang: Lang }) {
  const { messages, loading, send, retry, reset } = useChat();

  return (
    <div className="chat-view">
      <div className="chat-toolbar">
        <button className="chat-new" onClick={reset}>
          {strings.newChat[lang]}
        </button>
      </div>
      <MessageList messages={messages} loading={loading} lang={lang} onRetry={retry} />
      {messages.length === 0 && <PromptChips lang={lang} onPick={send} />}
      <ChatInput lang={lang} disabled={loading} onSend={send} />
    </div>
  );
}
