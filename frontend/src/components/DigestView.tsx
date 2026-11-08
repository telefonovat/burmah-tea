import { RefreshCw } from "lucide-react";
import { useState } from "react";
import { useDigest } from "../hooks/useDigest";
import { dateLabel, strings } from "../strings";
import type { Lang } from "../types";
import CategorySection from "./CategorySection";
import Skeleton from "./Skeleton";
import { PixelNewspaper, PixelTeaGlass } from "./icons";

export default function DigestView({ lang }: { lang: Lang }) {
  const state = useDigest();
  // Bumping roll re-mounts the sections, re-rolling their random picks.
  const [roll, setRoll] = useState(0);

  if (state.status === "loading") {
    return (
      <main>
        <Skeleton />
        <Skeleton />
        <Skeleton />
      </main>
    );
  }
  if (state.status === "error") {
    return <p className="empty">{strings.digestError[lang]}</p>;
  }

  const { digest } = state;
  const tea = digest.stories.filter((s) => s.tags.includes("tea"));
  const news = digest.stories.filter((s) => !s.tags.includes("tea"));

  return (
    <main>
      <div className="meta">
        <span className="date">{dateLabel(digest.date, lang)}</span>
        <button
          className="shuffle"
          onClick={() => setRoll((r) => r + 1)}
          aria-label={strings.shuffle[lang]}
          title={strings.shuffle[lang]}
        >
          <RefreshCw size={15} aria-hidden="true" />
        </button>
      </div>
      {tea.length > 0 && (
        <CategorySection
          key={`tea-${roll}`}
          title={strings.sectionTea[lang]}
          icon={<PixelTeaGlass className="section-icon" />}
          variant="tea"
          stories={tea}
          lang={lang}
        />
      )}
      {news.length > 0 && (
        <CategorySection
          key={`news-${roll}`}
          title={strings.sectionNews[lang]}
          icon={<PixelNewspaper className="section-icon" />}
          variant="news"
          stories={news}
          lang={lang}
        />
      )}
    </main>
  );
}
