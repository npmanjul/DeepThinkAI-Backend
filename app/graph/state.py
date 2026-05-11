from typing import TypedDict, List, Optional, Literal, Annotated, Any
from app.schemas.blog_schema import EvidenceItem, Plan
import operator

class State(TypedDict):
    topic: str
    mode: str
    needs_research: bool
    queries: List[str]
    evidence: List[EvidenceItem]
    plan: Optional[Plan]
    sections: Annotated[List[tuple[int, str]], operator.add]
    merged_md: str
    md_with_placeholders: str
    image_specs: List[dict]
    final: str
    user_id: Optional[str]
    db: Optional[Any]
