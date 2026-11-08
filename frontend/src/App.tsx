import { useEffect, useState } from "react";
import type { Story, View } from "./types";
import StoryCard from "./components/StoryCard";
import ViewSwitcher from "./components/ViewSwitcher";
import SiteHeader from "./components/SiteHeader";

function dateLabel(view: View): string {
  const d = new Date();
  if (view === "yesterday") d.setDate(d.getDate() - 1);
  return d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
}

export default function App() {
  const [view, setView] = useState<View>("today");
  const [digests, setDigests] = useState<Partial<Record<View, Story[]>>>({});
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load(view: View) {
      setError(false);
      try {
        const res = await fetch(`/api/digest/${view}`);
        if (!res.ok) throw new Error(String(res.status));
        const data: Story[] = await res.json();
        if (!cancelled) setDigests((d) => ({ ...d, [view]: data }));
      } catch {
        if (!cancelled) setError(true);
      }
    }

    if (!digests[view]) load(view);
    return () => {
      cancelled = true;
    };
  }, [view, digests]);

  const stories = digests[view] ?? [];

  return (
    <>
      <SiteHeader />

      <div className="container">
        <ViewSwitcher view={view} onSelect={setView} />

        <main>
          <p className="meta">
            <span className="date">{dateLabel(view)}</span>
          </p>
          {error && <p className="chat-hint">ဒေတာ မရရှိပါ။ Backend လည်ပတ်နေပါသလား?</p>}
          {!error && stories.length === 0 && <p className="chat-hint">…</p>}
          {stories.map((story) => (
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
