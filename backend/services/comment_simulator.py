import random
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.models.sim_models import SimCreator, SimContent, SimComment, SimActivityLog
from backend.models.core_models import AudienceCommentSignal
from backend.services.demand_scoring import record_comment_signal_and_rollup


FOOD_COMMENTS = [
    "Where can I buy this ragi/millet mix? Drop the link please!",
    "How much protein per serving does this bowl have?",
    "Do you have a discount code for this pantry brand?",
    "Can you share the exact gram measurements for this recipe?",
    "Is this oil good for high-heat Indian cooking too?",
    "Where to get clean oats without added sugar? Need this!",
    "Please make a lunchbox prep version of this next week!",
    "What is the price of this pack and do they ship pan-India?",
    "Can I swap dahi with Greek yogurt or hung curd here?",
    "Stock keeps running out on this—any restock update?",
    "Loved how quick this looked, definitely trying this tomorrow morning.",
    "Does this stay fresh in the fridge for 3 days for meal prep?",
]

BEAUTY_COMMENTS = [
    "Where to buy this cleanser? Link please!",
    "Is this fragrance-free enough for sensitive skin?",
    "What is the price and is there any coupon code?",
    "Can you do a texture test for oily skin in humid weather?",
]

FITNESS_COMMENTS = [
    "Where can I order these resistance bands? Drop the link!",
    "How heavy are these dumbbells and what is the price?",
    "Can you show a beginner modification for this mobility drill?",
    "Any discount code available on this recovery gear?",
]

HOME_COMMENTS = [
    "Where to get this brass lamp or ceramic piece? Link please!",
    "What is the price and do they deliver safely without breakage?",
    "Would this size fit a small study corner or shelf?",
    "Please share the care routine to keep brass shining!",
]

TECH_COMMENTS = [
    "Link for this desk lamp / keyboard under budget please!",
    "What is the price and is it available on sale right now?",
    "Does this work smoothly with Mac and Windows both?",
    "Can you share your full study setup checklist?",
]

COMMENT_POOLS = {
    "food": FOOD_COMMENTS,
    "healthy food & nutrition": FOOD_COMMENTS,
    "beauty": BEAUTY_COMMENTS,
    "beauty & skincare": BEAUTY_COMMENTS,
    "fitness": FITNESS_COMMENTS,
    "fitness & wellness": FITNESS_COMMENTS,
    "home": HOME_COMMENTS,
    "home & lifestyle": HOME_COMMENTS,
    "tech": TECH_COMMENTS,
    "tech & productivity": TECH_COMMENTS,
}

VIEWER_HANDLES = [
    "@aarav_kulkarni", "@meera_nair", "@rohan_desai", "@ananya_iyer",
    "@kabir_malhotra", "@tanya_menon", "@dev_patil", "@shruti_hegde",
    "@arjun_rao", "@neha_kapoor", "@aditya_joshi", "@kavya_shetty",
]


def _pool_for_content(content: SimContent) -> List[str]:
    cat = (content.category or (content.creator.niche if content.creator else "") or "").strip().lower()
    for key, pool in COMMENT_POOLS.items():
        if key in cat:
            return pool
    return FOOD_COMMENTS + BEAUTY_COMMENTS + FITNESS_COMMENTS + HOME_COMMENTS + TECH_COMMENTS


def generate_live_comment(
    sim_db: Session,
    core_db: Optional[Session] = None,
    category: Optional[str] = None,
    content_id: Optional[int] = None,
    custom_text: Optional[str] = None,
    author_handle: Optional[str] = None,
) -> Optional[dict]:
    """Create a realistic incoming comment on a matching post (prioritizing food when requested)."""
    query = sim_db.query(SimContent)
    if content_id is not None:
        query = query.filter(SimContent.id == content_id)
    elif category:
        cat_clean = category.strip().lower()
        if cat_clean == "food":
            query = query.filter(
                (SimContent.category.ilike("%food%"))
                | (SimContent.content_slug.ilike("%food%"))
                | (SimContent.caption.ilike("%food%"))
            )
        else:
            query = query.filter(
                (SimContent.category.ilike(f"%{cat_clean}%"))
                | (SimContent.content_slug.ilike(f"%{cat_clean}%"))
            )

    candidates = query.all()
    if not candidates and category:
        candidates = sim_db.query(SimContent).all()
    if not candidates:
        return None

    content = random.choice(candidates)
    pool = _pool_for_content(content)
    text = custom_text.strip() if custom_text else random.choice(pool)
    handle = author_handle.strip() if author_handle else random.choice(VIEWER_HANDLES)

    comment = SimComment(
        content_id=content.id,
        author_handle=handle,
        text=text,
        intent_label="general",
        created_at=datetime.utcnow(),
    )
    sim_db.add(comment)
    sim_db.flush()

    content.comments_count = (content.comments_count or 0) + 1
    sim_db.add(
        SimActivityLog(
            creator_id=content.creator_id,
            event_type="live_comment",
            description=f"{handle} commented on {content.content_slug}: {text}",
        )
    )
    sim_db.commit()
    sim_db.refresh(comment)

    rollup = None
    if core_db is not None:
        rollup = record_comment_signal_and_rollup(sim_db, core_db, comment, content)

    return {
        "comment_id": comment.id,
        "content_id": content.id,
        "content_slug": content.content_slug,
        "creator_id": content.creator_id,
        "category": content.category,
        "author_handle": comment.author_handle,
        "text": comment.text,
        "created_at": comment.created_at.isoformat(),
        "rollup": rollup,
    }


def seed_realistic_food_and_feed_comments(
    sim_db: Session,
    core_db: Optional[Session] = None,
    comments_per_food_post: int = 5,
    comments_per_other_post: int = 2,
) -> dict:
    """Populate realistic ongoing-style comments across food and other posts."""
    posts = sim_db.query(SimContent).order_by(SimContent.id.asc()).all()
    added = 0
    food_posts_touched = 0

    for post in posts:
        is_food = (
            "food" in (post.category or "").lower()
            or "food" in (post.content_slug or "").lower()
        )
        target_count = comments_per_food_post if is_food else comments_per_other_post
        if is_food:
            food_posts_touched += 1

        pool = _pool_for_content(post)
        existing_count = sim_db.query(SimComment).filter(SimComment.content_id == post.id).count()
        needed = max(0, target_count - existing_count)

        for idx in range(needed):
            minutes_ago = (needed - idx) * random.randint(2, 18)
            comment = SimComment(
                content_id=post.id,
                author_handle=random.choice(VIEWER_HANDLES),
                text=random.choice(pool),
                intent_label="general",
                created_at=datetime.utcnow() - timedelta(minutes=minutes_ago),
            )
            sim_db.add(comment)
            sim_db.flush()
            added += 1

            if core_db is not None:
                record_comment_signal_and_rollup(sim_db, core_db, comment, post)

        post.comments_count = sim_db.query(SimComment).filter(SimComment.content_id == post.id).count()

    sim_db.commit()
    return {
        "posts_scanned": len(posts),
        "food_posts_touched": food_posts_touched,
        "new_comments_added": added,
    }
