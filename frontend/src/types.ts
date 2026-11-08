// Mirrors the backend digest schema (schema_version 1), see backend/src/backend/models.py.

export interface StorySource {
  source_id: string;
  source_name: string;
  source_tier: "trustworthy" | "subpar" | "tabloid" | "celebrity";
  post_url: string;
}

export interface Story {
  id: string;
  title: string;
  summary: string;
  // English rendering; empty when absent. UI falls back to the Burmese fields.
  title_en: string;
  summary_en: string;
  tags: string[]; // "confirmed" | "popular" | "tea"
  sources: StorySource[];
  engagement: number;
  first_seen: string;
  last_updated: string;
}

export interface Digest {
  schema_version: number;
  date: string;
  generated_at: string;
  stories: Story[];
}

export type Tab = "digest" | "chat";
export type Lang = "mm" | "en";
