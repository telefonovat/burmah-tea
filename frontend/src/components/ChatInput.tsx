import { useRef, useState } from "react";
import { strings } from "../strings";
import type { Lang } from "../types";

export default function ChatInput({
  lang,
  disabled,
  onSend,
}: {
  lang: Lang;
  disabled: boolean;
  onSend: (text: string) => void;
}) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  function autogrow() {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  function submit() {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
    requestAnimationFrame(() => {
      if (ref.current) ref.current.style.height = "auto";
    });
  }

  return (
    <div className="chat-input-row">
      <textarea
        ref={ref}
        rows={1}
        value={value}
        disabled={disabled}
        onChange={(e) => {
          setValue(e.target.value);
          autogrow();
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
        placeholder={strings.inputPlaceholder[lang]}
      />
      <button onClick={submit} disabled={disabled || !value.trim()} aria-label="Send">
        ➤
      </button>
    </div>
  );
}
