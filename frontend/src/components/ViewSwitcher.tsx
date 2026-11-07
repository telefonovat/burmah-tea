import type { View } from "../types";

export default function ViewSwitcher({
  view,
  onSelect,
}: {
  view: View;
  onSelect: (view: View) => void;
}) {
  return (
    <nav className="view-switch">
      <button
        className={view === "today" ? "active" : ""}
        onClick={() => onSelect("today")}
      >
        ဒီနေ့ (Today)
      </button>
      <button
        className={view === "yesterday" ? "active" : ""}
        onClick={() => onSelect("yesterday")}
      >
        မနေ့ (Yesterday)
      </button>
    </nav>
  );
}
