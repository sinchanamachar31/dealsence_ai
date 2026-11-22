from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.database.sim_db import Base


class SimCreator(Base):
    __tablename__ = "sim_creators"

    id = Column(Integer, primary_key=True)
    handle = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    login_email = Column(String, unique=True, nullable=True)
    niche = Column(String, nullable=False, index=True)
    platform = Column(String, default="instagram")
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    follower_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    is_demo_creator = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    contents = relationship(
        "SimContent",
        back_populates="creator",
        cascade="all, delete-orphan",
    )


class SimContent(Base):
    __tablename__ = "sim_content"

    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey("sim_creators.id"), nullable=False, index=True)
    content_slug = Column(String, unique=True, nullable=False, index=True)
    media_type = Column(String, nullable=False)
    category = Column(String, nullable=True)
    thumbnail_path = Column(String, nullable=False)
    video_path = Column(String, nullable=True)
    caption = Column(Text, nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    posted_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("SimCreator", back_populates="contents")
    comments = relationship(
        "SimComment",
        back_populates="content",
        cascade="all, delete-orphan",
    )


class SimComment(Base):
    __tablename__ = "sim_comments"

    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey("sim_content.id"), nullable=False, index=True)
    author_handle = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    intent_label = Column(String, default="general")
    created_at = Column(DateTime, default=datetime.utcnow)

    content = relationship("SimContent", back_populates="comments")


class SimActivityLog(Base):
    __tablename__ = "sim_activity_logs"

    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey("sim_creators.id"), nullable=True)
    event_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
