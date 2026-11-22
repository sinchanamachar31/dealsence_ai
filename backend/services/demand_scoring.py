import re
from datetime import datetime
from typing import Dict, Tuple
from sqlalchemy.orm import Session

from backend.models.sim_models import SimCreator, SimContent, SimComment
from backend.models.core_models import AudienceCommentSignal, DemandSnapshot


HIGH_INTENT_PATTERNS = [
    r"\bbuy\b",
    r"\bpurchase\b",
    r"\border\b",
    r"\bprice\b",
    r"\bcost\b",
    r"\bhow much\b",
    r"\blink\b",
    r"\bwhere to (get|buy|find)\b",
    r"\bdiscount\b",
    r"\bcoupon\b",
    r"\bcode\b",
    r"\bstock\b",
    r"\brestock\b",
    r"\bavailable\b",
    r"\bship(ping)?\b",
    r"\bneed this\b",
    r"\bwant this\b",
]

REQUEST_PATTERNS = [
    r"\bcan you\b",
    r"\bcould you\b",
    r"\bplease (make|review|try|share|drop)\b",
    r"\bnext (video|reel|post)\b",
    r"\bshade\b",
    r"\bskin\b",
    r"\bsensitive\b",
    r"\bsize\b",
    r"\bvariant\b",
]


def score_comment_text(comment_text: str) -> Tuple[str, float, bool]:
    """Return (intent_label, demand_points, is_high_intent) for a comment."""
    text = (comment_text or "").strip().lower()
    if not text:
        return "general", 0.5, False

    has_purchase = any(re.search(p, text) for p in [
        r"\bbuy\b", r"\bpurchase\b", r"\border\b", r"\bneed this\b", r"\bwant this\b",
        r"\bstock\b", r"\brestock\b", r"\bavailable\b",
    ])
    has_price_or_link = any(re.search(p, text) for p in [
        r"\bprice\b", r"\bcost\b", r"\bhow much\b", r"\blink\b",
        r"\bwhere to (get|buy|find)\b", r"\bdiscount\b", r"\bcoupon\b", r"\bcode\b", r"\bship(ping)?\b",
    ])
    has_request = any(re.search(p, text) for p in REQUEST_PATTERNS)

    if has_purchase:
        return "purchase_intent", 4.0, True
    if has_price_or_link:
        return "pricing_or_link", 3.0, True
    if has_request:
        return "product_request", 2.0, True
    if "?" in text:
        return "question", 1.5, False
    return "general", 1.0, False


def compute_creator_demand_metrics(sim_db: Session, creator_id: int) -> Dict:
    """Compute live engagement & comment-demand metrics for a creator from sim_db."""
    creator = sim_db.query(SimCreator).filter(SimCreator.id == creator_id).first()
    if not creator:
        return {}

    posts = sim_db.query(SimContent).filter(SimContent.creator_id == creator_id).all()
    post_ids = [p.id for p in posts]

    comments = (
        sim_db.query(SimComment)
        .filter(SimComment.content_id.in_(post_ids))
        .all()
        if post_ids else []
    )

    total_comments = len(comments)
    high_intent_count = 0
    weighted_demand_sum = 0.0

    for c in comments:
        intent, points, is_hi = score_comment_text(c.text)
        if c.intent_label != intent:
            c.intent_label = intent
        if is_hi:
            high_intent_count += 1
        weighted_demand_sum += points

    total_views = sum(max(p.views or 0, 0) for p in posts)
    total_likes = sum(max(p.likes or 0, 0) for p in posts)
    for p in posts:
        p.comments_count = sum(1 for c in comments if c.content_id == p.id)

    denominator = max(total_views, creator.follower_count, 1)
    live_engagement_rate = round((total_likes + total_comments * 2.0) / denominator, 4)
    creator.engagement_rate = live_engagement_rate

    # Normalize demand score on a 0-100 scale
    raw_demand = (weighted_demand_sum * 3.5) + (high_intent_count * 6.0)
    demand_score = round(min(100.0, raw_demand), 2)

    return {
        "creator": creator,
        "niche": creator.niche or "general",
        "followers": creator.follower_count or 0,
        "engagement_rate": live_engagement_rate,
        "total_comments": total_comments,
        "high_intent_comments": high_intent_count,
        "demand_score": demand_score,
    }


def record_comment_signal_and_rollup(
    sim_db: Session,
    core_db: Session,
    comment: SimComment,
    content: SimContent,
) -> Dict:
    """Score a SimComment, save signal in core_db, and refresh creator & category snapshots."""
    intent_label, demand_points, is_high_intent = score_comment_text(comment.text)
    comment.intent_label = intent_label
    category = (content.category or (content.creator.niche if content.creator else None) or "general").strip()

    existing_signal = (
        core_db.query(AudienceCommentSignal)
        .filter(AudienceCommentSignal.sim_comment_id == comment.id)
        .first()
    )
    if existing_signal:
        existing_signal.intent_label = intent_label
        existing_signal.demand_points = demand_points
        existing_signal.is_high_intent = is_high_intent
        existing_signal.comment_text = comment.text
    else:
        core_db.add(
            AudienceCommentSignal(
                sim_comment_id=comment.id,
                sim_post_id=content.id,
                sim_creator_id=content.creator_id,
                category=category,
                author_handle=comment.author_handle,
                comment_text=comment.text,
                intent_label=intent_label,
                demand_points=demand_points,
                is_high_intent=is_high_intent,
            )
        )

    metrics = compute_creator_demand_metrics(sim_db, content.creator_id)
    sim_db.commit()

    # Upsert creator snapshot in core_db
    creator_snap = (
        core_db.query(DemandSnapshot)
        .filter(
            DemandSnapshot.scope_type == "creator",
            DemandSnapshot.scope_key == str(content.creator_id),
        )
        .first()
    )
    if not creator_snap:
        creator_snap = DemandSnapshot(
            scope_type="creator",
            scope_key=str(content.creator_id),
            category=category,
        )
        core_db.add(creator_snap)

    creator_snap.category = category
    creator_snap.total_comments = metrics.get("total_comments", 0)
    creator_snap.high_intent_comments = metrics.get("high_intent_comments", 0)
    creator_snap.demand_score = metrics.get("demand_score", 0.0)
    creator_snap.engagement_rate = metrics.get("engagement_rate", 0.0)
    creator_snap.updated_at = datetime.utcnow()

    # Roll up category snapshot across all signals in category
    cat_signals = (
        core_db.query(AudienceCommentSignal)
        .filter(AudienceCommentSignal.category == category)
        .all()
    )
    cat_total = len(cat_signals)
    cat_high = sum(1 for s in cat_signals if s.is_high_intent)
    cat_points = sum(s.demand_points for s in cat_signals)
    cat_score = round(min(100.0, (cat_points * 2.5) + (cat_high * 5.0)), 2)

    cat_snap = (
        core_db.query(DemandSnapshot)
        .filter(
            DemandSnapshot.scope_type == "category",
            DemandSnapshot.scope_key == category.lower(),
        )
        .first()
    )
    if not cat_snap:
        cat_snap = DemandSnapshot(
            scope_type="category",
            scope_key=category.lower(),
            category=category,
        )
        core_db.add(cat_snap)

    cat_snap.category = category
    cat_snap.total_comments = cat_total
    cat_snap.high_intent_comments = cat_high
    cat_snap.demand_score = cat_score
    cat_snap.updated_at = datetime.utcnow()

    core_db.commit()

    return {
        "comment_id": comment.id,
        "intent_label": intent_label,
        "demand_points": demand_points,
        "is_high_intent": is_high_intent,
        "creator_metrics": {
            "creator_id": content.creator_id,
            "total_comments": metrics.get("total_comments", 0),
            "high_intent_comments": metrics.get("high_intent_comments", 0),
            "demand_score": metrics.get("demand_score", 0.0),
            "engagement_rate": metrics.get("engagement_rate", 0.0),
        },
        "category_snapshot": {
            "category": category,
            "total_comments": cat_total,
            "high_intent_comments": cat_high,
            "demand_score": cat_score,
        },
    }
