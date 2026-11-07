export interface Story {
  title: string;
  summary: string;
  url: string;
  page_name: string;
  page_url: string;
  engagement: number;
  tag: "[reported]" | "[confirmed]";
}

export type View = "today" | "yesterday";
