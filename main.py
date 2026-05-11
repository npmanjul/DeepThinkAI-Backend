from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.auth import auth_router
from app.api.v1.endpoints.blog import blog_router
from app.core.database import engine
from app.core.database import Base
from sqlalchemy import inspect, text
from app.middlewares.auth_middleware import AuthMiddleware


app = FastAPI(title="DeepThink")

app.add_middleware(AuthMiddleware)


def ensure_blog_user_id_column() -> None:
    inspector = inspect(engine)
    if "blogs" not in inspector.get_table_names():
        return

    blog_columns = {column["name"] for column in inspector.get_columns("blogs")}
    if "user_id" in blog_columns:
        return

    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE blogs ADD COLUMN user_id VARCHAR"))


ensure_blog_user_id_column()
Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      
    allow_credentials=True,
    allow_methods=["*"],      
    allow_headers=["*"],  
)

app.include_router(auth_router,prefix="/api/v1")
app.include_router(blog_router,prefix="/api/v1")