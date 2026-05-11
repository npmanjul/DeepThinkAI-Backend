from app.graph.state import State
from app.schemas.blog_schema import RouterDecision
from langchain_core.messages import SystemMessage,HumanMessage
from app.llms.llm import llm_mistral,llm
from app.prompts.prompts import ROUTER_SYSTEM,RESEARCH_SYSTEM,ORCH_SYSTEM,WORKER_SYSTEM,DECIDE_IMAGES_SYSTEM
from typing import List
from app.schemas.blog_schema import EvidenceItem,Plan,EvidencePack,Task,GlobalImagePlan
from app.tools.tools import tavily_search,gemini_generate_image_bytes
from langgraph.types import Send
from pathlib import Path
from app.llms.llm import llm_google, llm_mistral,llm


def router_node(state: State) -> dict:
    topic = state["topic"]
    decider = llm_mistral.with_structured_output(RouterDecision)
    decision = decider.invoke(
        [
            SystemMessage(content=ROUTER_SYSTEM),
            HumanMessage(content=f"Topic: {topic}"),
        ]
    )

    return {
        "needs_research": decision.needs_research,
        "mode": decision.mode,
        "queries": decision.queries,
    }


def route_next(state: State) -> str:
    return "research" if state["needs_research"] else "orchestrator"


def research_node(state: State) -> dict:
    queries = (state.get("queries", []) or [])
    max_results = 6

    raw_results: List[dict] = []

    for q in queries:
        raw_results.extend(tavily_search(q, max_results=max_results))

    if not raw_results:
        return {"evidence": []}

    extractor = llm.with_structured_output(EvidencePack)
    pack = extractor.invoke(
        [
            SystemMessage(content=RESEARCH_SYSTEM),
            HumanMessage(content=f"Raw results:\n{raw_results}"),
        ]
    )

    # Deduplicate by URL
    dedup = {}
    for e in pack.evidence:
        if e.url:
            dedup[e.url] = e

    return {"evidence": list(dedup.values())}


def orchestrator_node(state: State) -> dict:
    planner = llm.with_structured_output(Plan)

    evidence = state.get("evidence", [])
    mode = state.get("mode", "closed_book")

    try:
        plan = planner.invoke(
            [
                SystemMessage(content=ORCH_SYSTEM),
                HumanMessage(
                    content=(
                        f"Topic: {state['topic']}\n"
                        f"Mode: {mode}\n\n"
                        f"Evidence (ONLY use for fresh claims; may be empty):\n"
                        f"{[e.model_dump() for e in evidence][:16]}"
                    )
                ),
            ]
        )
    except Exception as e:
        print(f"ERROR in orchestrator: {e}")
        raise

    return {"plan": plan}


def fanout(state: State):
    return [
        Send(
            "worker",
            {
                "task": task.model_dump(),
                "topic": state["topic"],
                "mode": state["mode"],
                "plan": state["plan"].model_dump(),
                "evidence": [e.model_dump() for e in state.get("evidence", [])],
            },
        )
        for task in state["plan"].tasks
    ]



def worker_node(payload: dict) -> dict:
    
    task = Task(**payload["task"])
    plan = Plan(**payload["plan"])
    evidence = [EvidenceItem(**e) for e in payload.get("evidence", [])]
    topic = payload["topic"]
    mode = payload.get("mode", "closed_book")

    bullets_text = "\n- " + "\n- ".join(task.bullets)

    evidence_text = ""
    if evidence:
        evidence_text = "\n".join(
            f"- {e.title} | {e.url} | {e.published_at or 'date:unknown'}".strip()
            for e in evidence[:20]
        )

    section_md = llm.invoke(
        [
            SystemMessage(content=WORKER_SYSTEM),
            HumanMessage(
                content=(
                    f"Blog title: {plan.blog_title}\n"
                    f"Audience: {plan.audience}\n"
                    f"Tone: {plan.tone}\n"
                    f"Blog kind: {plan.blog_kind}\n"
                    f"Constraints: {plan.constraints}\n"
                    f"Topic: {topic}\n"
                    f"Mode: {mode}\n\n"
                    f"Section title: {task.title}\n"
                    f"Goal: {task.goal}\n"
                    f"Target words: {task.target_words}\n"
                    f"Tags: {task.tags}\n"
                    f"requires_research: {task.requires_research}\n"
                    f"requires_citations: {task.requires_citations}\n"
                    f"requires_code: {task.requires_code}\n"
                    f"Bullets:{bullets_text}\n\n"
                    f"Evidence (ONLY use these URLs when citing):\n{evidence_text}\n"
                )
            ),
        ]
    ).content.strip()

    return {"sections": [(task.id, section_md)]}


def merge_content(state: State) -> dict:

    plan = state["plan"]

    ordered_sections = [md for _, md in sorted(state["sections"], key=lambda x: x[0])]
    body = "\n\n".join(ordered_sections).strip()
    merged_md = f"# {plan.blog_title}\n\n{body}\n"
    return {"merged_md": merged_md}




def decide_images(state: State) -> dict:
    planner = llm.with_structured_output(GlobalImagePlan)
    merged_md = state["merged_md"]
    plan = state["plan"]
    assert plan is not None

    image_plan = planner.invoke(
        [
            SystemMessage(content=DECIDE_IMAGES_SYSTEM),
            HumanMessage(
                content=(
                    f"Blog kind: {plan.blog_kind}\n"
                    f"Topic: {state['topic']}\n\n"
                    "Insert placeholders + propose image prompts.\n\n"
                    f"{merged_md}"
                )
            ),
        ]
    )

    return {
        "md_with_placeholders": image_plan.md_with_placeholders,
        "image_specs": [img.model_dump() for img in image_plan.images],
    }



def generate_and_place_images(state: State) -> dict:
    from app.models.model import Blog, BlogStatus
    import uuid
    import re

    plan = state["plan"]
    assert plan is not None

    md = state.get("md_with_placeholders") or state["merged_md"]
    image_specs = state.get("image_specs", []) or []
    user_id = state.get("user_id")
    db = state.get("db")

    # Process images in memory (no file writes)
    for spec in image_specs:
        placeholder = spec["placeholder"]
        try:
            img_bytes = gemini_generate_image_bytes(spec["prompt"])
            # In a real app, you'd upload to cloud storage (S3, etc.)
            # For now, just skip image generation and keep placeholder
        except Exception as e:
            # graceful fallback: keep doc usable
            prompt_block = (
                f"> **[IMAGE GENERATION FAILED]** {spec.get('caption','')}\n>\n"
                f"> **Alt:** {spec.get('alt','')}\n>\n"
                f"> **Prompt:** {spec.get('prompt','')}\n>\n"
                f"> **Error:** {e}\n"
            )
            md = md.replace(placeholder, prompt_block)
            continue

    # Save final blog to database
    if db and plan and user_id:
        try:
            # Create URL-friendly slug from title
            slug = re.sub(r'[^\w\s-]', '', plan.blog_title.lower())
            slug = re.sub(r'[\s_-]+', '-', slug)
            slug = slug.strip('-')

            # Ensure unique slug
            existing = db.query(Blog).filter(Blog.slug == slug).first()
            if existing:
                slug = f"{slug}-{str(uuid.uuid4())[:8]}"

            blog = Blog(
                id=str(uuid.uuid4()),
                slug=slug,
                title=plan.blog_title,
                content=md,
                is_published=False,
                status=BlogStatus.COMPLETED,
                user_id=user_id,
            )
            db.add(blog)
            db.commit()
            db.refresh(blog)
            print(f"Blog saved to database with ID: {blog.id}")
        except Exception as e:
            print(f"Error saving blog to database: {e}")
            db.rollback()

    return {"final": md}

