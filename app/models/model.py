import uuid
import enum
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    String,
    Boolean,
    ForeignKey,
    func,
    ARRAY,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


# Enums
class BlogStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELED = "canceled"


# User
class User(Base):
    __tablename__ = "users"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name = Column(String(50), nullable=False)
    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )
    password = Column(String, nullable=True)
    phone = Column(
        String(10),
        unique=True,
        index=True,
        nullable=True
    )
    is_google_auth = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    blogs = relationship("Blog", back_populates="user")


# OTP
class OTP(Base):
    __tablename__ = "otps"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    otp = Column(String(6), nullable=False)
    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )


# Blog
class Blog(Base):
    __tablename__ = "blogs"
    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    is_published = Column(Boolean, default=False)
    status = Column(
        Enum(BlogStatus),
        default=BlogStatus.PENDING,
        nullable=False
    )
    images = Column(
        ARRAY(String),
        nullable=True,
        default=[]
    )
    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False
    )
    user = relationship("User", back_populates="blogs")