import { useMemo } from "react";
import type { Lang, Story } from "../types";
import StoryCard from "./StoryCard";

// 3 stories at random from the top 10 by engagement.
// Re-rolls whenever the parent re-mounts the section (Shuffle button).
export default function CategorySection({
  title,
  stories,
  lang,
}: {
  title: string;
  stories: Story[];
  lang: Lang;
}) {
  const picked = useMemo(() => {
    const top = [...stories].sort((a, b) => b.engagement - a.engagement).slice(0, 10);
    // Intentionally impure: the random pick is the feature; memoized so
    // re-renders don't re-roll — only a fresh mount (Shuffle) does.
    // eslint-disable-next-line react/purity
    return [...top].sort(() => Math.random() - 0.5).slice(0, 3);
  }, [stories]);

  if (picked.length === 0) return null;

  return (
    <section className="category">
      <h2 className="category-title">{title}</h2>
      {picked.map((s) => (
        <StoryCard key={s.id} story={s} lang={lang} />
      ))}
    </section>
  );
}
