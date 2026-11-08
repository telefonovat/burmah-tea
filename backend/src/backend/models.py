"""Pydantic models: the one vocabulary for sources, posts, stories, digests."""

from typing import Literal

from pydantic import BaseModel, Field

Tier = Literal["trustworthy", "subpar", "tabloid", "celebrity"]


class Source(BaseModel):
    """A curated Facebook page. Tier is curation data, never code."""

    id: str
    name: str
    url: str
    tier: Tier


class Post(BaseModel):
    """A normalised Facebook post, as stored in posts.db."""

    post_id: str
    source_id: str
    source_name: str
    source_tier: Tier
    url: str
    text: str = Field(min_length=1)
    likes: int = 0
    comments: int = 0
    shares: int = 0
    engagement: int = 0
    timestamp: int = 0
    first_seen: str = ""
    last_updated: str = ""


class StorySource(BaseModel):
    """One source backing a story, with tier so consumers can hedge."""

    source_id: str
    source_name: str
    source_tier: Tier
    post_url: str


class Story(BaseModel):
    """A clustered topic in the digest."""

    id: str
    title: str
    summary: str
    tags: list[str] = []
    sources: list[StorySource]
    engagement: int
    first_seen: str
    last_updated: str


class Digest(BaseModel):
    """The day's digest, one versioned artifact for all consumers."""

    schema_version: int = 1
    date: str
    generated_at: str
    stories: list[Story]
