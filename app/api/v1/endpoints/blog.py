from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, Request
from app.schemas.blog_schema import BlogUpdateSchema
from app.controller import blog
from app.core.database import get_db
from sse_starlette import EventSourceResponse
import json
from app.services.stream_graph import parse_event
from app.graph.builder import app

blog_router = APIRouter(prefix="/blog", tags=["Blog"])

@blog_router.get("/stream")
async def stream_graph(topic: str, request: Request, db: Session = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        async def error_generator():
            yield {
                "event": "error",
                "data": json.dumps({"message": "Unauthorized: Please login to generate blogs"})
            }
        return EventSourceResponse(error_generator(), media_type="text/event-stream")

    user_id = user.get("sub") if isinstance(user, dict) else getattr(user, "sub", None)
    print(f"Authenticated user_id: {user_id} for topic: {topic}")

    async def event_generator():
        async for event in app.astream_events(
            {
                "topic": topic,
                "user_id": user_id,
                "db": db
            },
            version="v2"
        ):
            parsed = parse_event(event)
            if parsed:
                yield {
                    "event": "message",
                    "data": json.dumps(parsed)
                }

    return EventSourceResponse(event_generator(), media_type="text/event-stream")


@blog_router.get("/blog-history")
async def get_history(request: Request, db: Session = Depends(get_db)):
    return await blog.get_history(request, db)

@blog_router.get("/get-blog",status_code=status.HTTP_200_OK)
async def get_blog(blog_slug: str, request: Request, db: Session = Depends(get_db)):
    return await blog.get_blog(blog_slug, request, db)

@blog_router.get("/read-blog",status_code=status.HTTP_200_OK)
async def read_blog(blog_slug: str, db: Session = Depends(get_db)):
    return await blog.read_blog(blog_slug, db)


@blog_router.patch("/update-published",status_code=status.HTTP_200_OK)
async def update_published_status(update_data: BlogUpdateSchema, request: Request, db: Session = Depends(get_db)):
    return await blog.update_published_status(update_data, request, db)

@blog_router.delete("/delete-blog",status_code=status.HTTP_200_OK)
async def delete_blog(blog_slug: str, request: Request, db: Session = Depends(get_db)):
    return await blog.delete_blog(blog_slug, request, db)