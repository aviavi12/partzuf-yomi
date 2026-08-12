from datetime import datetime
from pydantic import BaseModel


class NewsArticleBase(BaseModel):
    headline: str
    summary: str | None = None
    content: str | None = None
    url: str | None = None
    language: str = "he"
    published_at: datetime | None = None


class NewsArticleResponse(NewsArticleBase):
    id: str
    source_id: str
    source_name: str | None = None
    external_id: str | None = None
    collected_at: datetime
    content_hash: str
    is_demo: bool
    is_analyzed: bool
    cluster_id: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NewsArticleListResponse(BaseModel):
    items: list[NewsArticleResponse]
    total: int
    page: int
    page_size: int
