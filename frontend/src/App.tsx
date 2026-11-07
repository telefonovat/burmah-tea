import { useState } from "react";
import todayData from "./data/digest.today.json";
import yesterdayData from "./data/digest.yesterday.json";
import type { Story, View } from "./types";
import StoryCard from "./components/StoryCard";
import ViewSwitcher from "./components/ViewSwitcher";

const digests: Record<View, Story[]> = {
  today: todayData as Story[],
  yesterday: yesterdayData as Story[],
};

function dateLabel(view: View): string {
  const d = new Date();
  if (view === "yesterday") d.setDate(d.getDate() - 1);
  return d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
}

export default function App() {
  const [view, setView] = useState<View>("today");

  return (
    <>
      <header>
        <div className="container">
          <h1>
            Burmahtea<span className="dot">.</span>com
          </h1>
          <p className="tagline">မြန်မာ ဖေ့စ်ဘွတ်ခ်မှ နောက်ဆုံး သတင်းများ</p>
        </div>
      </header>

      <div className="container">
        <ViewSwitcher view={view} onSelect={setView} />

        <main>
          <p className="meta">
            <span className="date">{dateLabel(view)}</span>
          </p>
          {digests[view].map((story) => (
            <StoryCard key={story.url} story={story} />
          ))}
        </main>
      </div>

      <footer>
        <div className="container">
          <p>Burmahtea.com – မြန်မာ ဖေ့စ်ဘွတ်ခ် နေ့စဉ် ဒိုင်းဂျက်။</p>
        </div>
      </footer>
    </>
  );
}
