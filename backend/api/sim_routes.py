import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import or_

from backend.database.sim_db import get_sim_db as get_db
from backend.models.sim_models import (
    SimActivityLog,
    SimComment,
    SimContent,
    SimCreator,
)


router = APIRouter(prefix="/api/sim", tags=["Simulation"])


class DemoAuthRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    email: Optional[str] = None


def _comment_payload(comment):
    return {
        "id": comment.id,
        "content_id": comment.content_id,
        "author_handle": comment.author_handle,
        "text": comment.text,
        "intent_label": comment.intent_label,
        "created_at": comment.created_at,
    }


def _content_payload(content, include_creator=False):
    payload = {
        "id": content.id,
        "creator_id": content.creator_id,
        "content_slug": content.content_slug,
        "media_type": content.media_type,
        "category": content.category,
        "thumbnail_path": content.thumbnail_path,
        "video_path": content.video_path,
        "caption": content.caption,
        "views": content.views,
        "likes": content.likes,
        "comments_count": content.comments_count,
        "posted_at": content.posted_at,
        "comments": [_comment_payload(comment) for comment in content.comments],
    }
    if include_creator:
        payload["creator"] = {
            "handle": content.creator.handle,
            "display_name": content.creator.display_name,
            "niche": content.creator.niche,
            "avatar_url": content.creator.avatar_url,
            "is_demo_creator": content.creator.is_demo_creator,
        }
    return payload


def _creator_payload(creator, include_contents=False):
    payload = {
        "id": creator.id,
        "handle": creator.handle,
        "display_name": creator.display_name,
        "login_email": creator.login_email,
        "niche": creator.niche,
        "platform": creator.platform,
        "bio": creator.bio,
        "avatar_url": creator.avatar_url,
        "follower_count": creator.follower_count,
        "engagement_rate": creator.engagement_rate,
        "is_demo_creator": creator.is_demo_creator,
        "created_at": creator.created_at,
    }
    if include_contents:
        payload["contents"] = [
            _content_payload(content) for content in creator.contents
        ]
    return payload


@router.get("/creators")
def list_creators(
    search: str | None = None,
    niche: str | None = None,
    is_demo: bool | None = None,
    limit: int = 120,
    db: Session = Depends(get_db),
    demo_only: bool | None = None,
):
    query = db.query(SimCreator)
    if is_demo is not None:
        query = query.filter(SimCreator.is_demo_creator == is_demo)
    elif demo_only:
        query = query.filter(SimCreator.is_demo_creator.is_(True))
    if niche is not None:
        query = query.filter(SimCreator.niche == niche)
    if search is not None and search.strip():
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                SimCreator.handle.ilike(search_pattern),
                SimCreator.display_name.ilike(search_pattern),
                SimCreator.niche.ilike(search_pattern),
            )
        )
    creators = query.order_by(
        SimCreator.is_demo_creator.desc(),
        SimCreator.follower_count.desc(),
    ).limit(limit).all()
    return [_creator_payload(creator) for creator in creators]


def _demo_session(auth_request: DemoAuthRequest):
    username = auth_request.username.strip()
    if not username:
        raise HTTPException(status_code=422, detail="Username must not be empty")
    display_name = username.replace("_", " ").replace(".", " ").title()
    return {
        "access_token": secrets.token_urlsafe(32),
        "username": username,
        "display_name": display_name,
        "role": "demo_user",
    }


@router.post("/auth/login")
def demo_login(auth_request: DemoAuthRequest):
    return _demo_session(auth_request)


@router.post("/auth/register")
def demo_register(auth_request: DemoAuthRequest):
    return _demo_session(auth_request)


@router.get("/creators/{handle}")
def get_creator(handle: str, db: Session = Depends(get_db)):
    normalized_handle = handle if handle.startswith("@") else f"@{handle}"
    creator = (
        db.query(SimCreator)
        .options(
            selectinload(SimCreator.contents).selectinload(SimContent.comments)
        )
        .filter(SimCreator.handle == normalized_handle)
        .first()
    )
    if creator is None:
        raise HTTPException(status_code=404, detail="Creator not found")
    return _creator_payload(creator, include_contents=True)


@router.get("/feed")
def get_feed(
    demo_only: bool = True,
    niche: str | None = None,
    media_type: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = (
        db.query(SimContent)
        .join(SimCreator)
        .options(
            joinedload(SimContent.creator),
            selectinload(SimContent.comments),
        )
    )
    if demo_only:
        query = query.filter(SimCreator.is_demo_creator.is_(True))
    if niche is not None:
        query = query.filter(SimCreator.niche == niche)
    if media_type is not None:
        query = query.filter(SimContent.media_type == media_type)
    contents = query.order_by(SimContent.posted_at.desc()).limit(limit).all()
    return [_content_payload(content, include_creator=True) for content in contents]


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "demo_creators": db.query(SimCreator)
        .filter(SimCreator.is_demo_creator.is_(True))
        .count(),
        "total_creators": db.query(SimCreator).count(),
        "total_contents": db.query(SimContent).count(),
        "total_comments": db.query(SimComment).count(),
    }
