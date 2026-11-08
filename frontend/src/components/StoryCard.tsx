import { TAG_LABEL, TIER_LABEL } from "../strings";
import type { Lang, Story } from "../types";

export default function StoryCard({ story, lang }: { story: Story; lang: Lang }) {
  // English text falls back to Burmese when the digest lacks the en fields.
  const title = (lang === "en" && story.title_en) || story.title;
  const summary = (lang === "en" && story.summary_en) || story.summary;

  return (
    <article className="story-card">
      <div className="story-tags">
        {story.tags.map((t) => (
          <span key={t} className={`chip chip-${t}`}>
            {TAG_LABEL[t]?.[lang] ?? t}
          </span>
        ))}
      </div>
      <h3 className="story-title">{title}</h3>
      <p className="story-summary">{summary}</p>
      <ul className="story-sources">
        {story.sources.map((src) => (
          <li key={src.source_id}>
            <a href={src.post_url} target="_blank" rel="noreferrer">
              {src.source_name}
            </a>
            <span className={`tier tier-${src.source_tier}`}>
              {TIER_LABEL[src.source_tier]?.[lang] ?? src.source_tier}
            </span>
          </li>
        ))}
      </ul>
    </article>
  );
}
