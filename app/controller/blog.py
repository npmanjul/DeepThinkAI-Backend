from operator import is_

from sqlalchemy.orm import Session
from fastapi import HTTPException, Request
from app.schemas.blog_schema import BlogUpdateSchema
from app.models.model import Blog, BlogStatus

async def get_history(request: Request, db: Session):
    user_id = request.state.user.get("sub")
    blogs = db.query(Blog).filter(Blog.user_id == user_id).order_by(Blog.created_at.desc()).all()
    
    return [
        {
            "id": blog.id,
            "title": blog.title,
            "created_at": blog.created_at.isoformat(),
            "slug": blog.slug,
            "is_published": blog.is_published,
            "status": blog.status,
        }
        for blog in blogs
    ]

async def get_blog(blog_slug: str, request: Request, db: Session):
    user_id = request.state.user.get("sub")
    blog = db.query(Blog).filter(Blog.slug == blog_slug, Blog.user_id == user_id).first()
    
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    return {
        "title": blog.title,
        "content": blog.content,
        "created_at": blog.created_at.isoformat(),
        "is_published": blog.is_published,
        "status": blog.status,
    }


async def read_blog(blog_slug: str, db: Session):
    blog = db.query(Blog).filter(Blog.slug == blog_slug).first()
    
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    # if not blog.is_published:
    #     raise HTTPException(status_code=403, detail="Blog is not published yet")
    
    if blog.status != BlogStatus.COMPLETED:
        raise HTTPException(status_code=403, detail="Blog generation is not completed yet")
    
    return {
        "title": blog.title,
        "content": blog.content,
        "created_at": blog.created_at.isoformat(),
        "is_published": blog.is_published,
        "status": blog.status,
    }

async def update_published_status(
    update_data: BlogUpdateSchema,
    request: Request, 
    db: Session
):
    user_id = request.state.user.get("sub")
    blog = db.query(Blog).filter(Blog.slug == update_data.blog_slug, Blog.user_id == user_id).first()
    
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    if blog.status != BlogStatus.COMPLETED:
        raise HTTPException(status_code=403, detail="Only completed blogs can be published or unpublished")
    
    blog.is_published = update_data.published
    db.commit()
    
    return {"message": f"Blog {'published' if update_data.published else 'unpublished'} successfully"}


async def delete_blog(blog_slug: str, request: Request, db: Session):
    user_id = request.state.user.get("sub")
    blog = db.query(Blog).filter(Blog.slug == blog_slug, Blog.user_id == user_id).first()
    
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    db.delete(blog)
    db.commit()
    
    return {"message": "Blog deleted successfully"}