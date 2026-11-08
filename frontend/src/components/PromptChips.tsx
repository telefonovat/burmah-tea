import { strings } from "../strings";
import type { Lang } from "../types";

export default function PromptChips({
  lang,
  onPick,
}: {
  lang: Lang;
  onPick: (text: string) => void;
}) {
  return (
    <div className="prompt-chips">
      <button onClick={() => onPick(strings.chipNews[lang])}>
        {strings.chipNews[lang]}
      </button>
      <button onClick={() => onPick(strings.chipTea[lang])}>
        {strings.chipTea[lang]}
      </button>
    </div>
  );
}
