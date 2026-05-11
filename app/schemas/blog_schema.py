from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal, Any
from datetime import datetime


def _coerce_bullet_item(item: Any) -> Optional[str]:
    """LLMs sometimes emit a bullet as a one-element list instead of a string."""
    if item is None:
        return None
    if isinstance(item, str):
        s = item.strip()
        return s if s else None
    if isinstance(item, list):
        parts: List[str] = []
        for x in item:
            nested = _coerce_bullet_item(x)
            if nested:
                parts.append(nested)
        if not parts:
            return None
        return " ".join(parts)
    s = str(item).strip()
    return s if s else None


class NodeEvent(BaseModel):
    node_name: str
    status: str
    message: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration: Optional[float] = None
    output: Optional[str] = None


class Task(BaseModel):
    id: int
    title: str

    goal: str = Field(
        ...,
        description="One sentence describing what the reader should be able to do/understand after this section.",
    )
    bullets: List[str] = Field(
        ...,
        min_length=3,
        max_length=6,
        description="1-3 concrete, non-overlapping subpoints to cover in this section.",
    )
    target_words: int = Field(..., description="Target word count for this section (120–550).")

    tags: List[str] = Field(default_factory=list)
    requires_research: bool = False
    requires_citations: bool = False
    requires_code: bool = False

    @field_validator("bullets", mode="before")
    @classmethod
    def normalize_bullets(cls, v: Any) -> List[str]:
        if v is None:
            return []
        if not isinstance(v, list):
            coerced = _coerce_bullet_item(v)
            return [coerced] if coerced else []
        out: List[str] = []
        for item in v:
            coerced = _coerce_bullet_item(item)
            if coerced:
                out.append(coerced)
        return out


class Plan(BaseModel):
    blog_title: str
    audience: str
    tone: str
    blog_kind: Literal["explainer", "tutorial", "news_roundup", "comparison", "system_design"] = "explainer"
    constraints: List[str] = Field(default_factory=list)
    tasks: List[Task]


class EvidenceItem(BaseModel):
    title: str
    url: str
    published_at: Optional[str] = None
    snippet: Optional[str] = None
    source: Optional[str] = None


class RouterDecision(BaseModel):
    needs_research: bool
    mode: Literal["closed_book", "hybrid", "open_book"]
    queries: List[str] = Field(default_factory=list)


class EvidencePack(BaseModel):
    evidence: List[EvidenceItem] = Field(default_factory=list)


class ImageSpec(BaseModel):
    placeholder: str = Field(..., description="e.g. [[IMAGE_1]]")
    filename: str = Field(..., description="Save under images/, e.g. qkv_flow.png")
    alt: str
    caption: str
    prompt: str = Field(..., description="Prompt to send to the image model.")
    size: Literal["1024x1024", "1024x1536"] = "1024x1024"
    quality: Literal["low", "medium", "high"] = "medium"


class GlobalImagePlan(BaseModel):
    md_with_placeholders: str
    images: List[ImageSpec] = Field(default_factory=list)

class BlogUpdateSchema(BaseModel):
    blog_slug: str
    published: Optional[bool] = None
