import type { Story } from "../types";

export default function StoryCard({ story }: { story: Story }) {
  const confirmed = story.tag === "[confirmed]";
  return (
    <article id={`story-${story.title}`} className="story-card">
      <div className="story-header">
        <h2>
          <a href={story.url}>{story.title}</a>
        </h2>
        <span className={`badge ${confirmed ? "badge-confirmed" : "badge-reported"}`}>
          {story.tag}
        </span>
      </div>
      <p className="engagement">
        <span className="engagement-count">❤️ {story.engagement}</span>
      </p>
      <div className="summary">{story.summary}</div>
      <p className="source">
        <span>Source:</span> <a href={story.page_url}>{story.page_name}</a>
      </p>
    </article>
  );
}
