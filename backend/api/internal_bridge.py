from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.core_db import get_core_db
from backend.database.sim_db import get_sim_db
from backend.models.core_models import (
    AudienceCommentSignal,
    CreatorPromotionListing,
    DemandSnapshot,
)
from backend.models.sim_models import SimComment, SimContent, SimCreator
from backend.services.demand_scoring import (
    compute_creator_demand_metrics,
    score_comment_text,
)


router = APIRouter(prefix="/api/internal", tags=["Internal"])


def _upsert_creator_snapshot(core_db: Session, metrics: dict) -> None:
    creator = metrics["creator"]
    snapshot = (
        core_db.query(DemandSnapshot)
        .filter(
            DemandSnapshot.scope_type == "creator",
            DemandSnapshot.scope_key == str(creator.id),
        )
        .first()
    )
    if snapshot is None:
        snapshot = DemandSnapshot(
            scope_type="creator",
            scope_key=str(creator.id),
            category=metrics["niche"],
        )
        core_db.add(snapshot)

    snapshot.category = metrics["niche"]
    snapshot.total_comments = metrics["total_comments"]
    snapshot.high_intent_comments = metrics["high_intent_comments"]
    snapshot.demand_score = metrics["demand_score"]
    snapshot.engagement_rate = metrics["engagement_rate"]
    snapshot.updated_at = datetime.utcnow()


def sync_creator_promotion_listing(
    sim_db: Session,
    core_db: Session,
    creator_id: int,
) -> CreatorPromotionListing | None:
    metrics = compute_creator_demand_metrics(sim_db, creator_id)
    if not metrics:
        return None

    creator = metrics["creator"]
    listing = (
        core_db.query(CreatorPromotionListing)
        .filter(CreatorPromotionListing.sim_creator_id == creator_id)
        .first()
    )
    if listing is None:
        listing = CreatorPromotionListing(
            sim_creator_id=creator_id,
            promotion_status="available",
            available_for_promo=True,
        )
        core_db.add(listing)

    engagement_rate = max(metrics["engagement_rate"], 0.0)
    listing.creator_handle = creator.handle
    listing.creator_name = creator.display_name
    listing.niche = metrics["niche"]
    listing.followers = metrics["followers"]
    listing.engagement_rate = metrics["engagement_rate"]
    listing.total_comments_tracked = metrics["total_comments"]
    listing.high_intent_comments = metrics["high_intent_comments"]
    listing.audience_demand_score = metrics["demand_score"]
    listing.promotion_fit_score = round(
        min(100.0, metrics["demand_score"] * 0.8 + min(engagement_rate * 100, 20)),
        2,
    )
    listing.recommended_fee = round(
        max(250.0, min(50000.0, metrics["followers"] * engagement_rate * 0.5)),
        2,
    )
    listing.updated_at = datetime.utcnow()
    return listing


@router.post("/comments/sync")
def sync_comments(
    sim_db: Session = Depends(get_sim_db),
    core_db: Session = Depends(get_core_db),
):
    comment_rows = (
        sim_db.query(SimComment, SimContent)
        .join(SimContent, SimComment.content_id == SimContent.id)
        .order_by(SimComment.id.asc())
        .all()
    )
    if not comment_rows:
        return {
            "synced_comments": 0,
            "creator_snapshots_updated": 0,
            "category_snapshots_updated": 0,
        }

    comment_ids = [comment.id for comment, _ in comment_rows]
    signal_by_comment_id = {
        signal.sim_comment_id: signal
        for signal in core_db.query(AudienceCommentSignal)
        .filter(AudienceCommentSignal.sim_comment_id.in_(comment_ids))
        .all()
    }
    creators = {
        creator.id: creator
        for creator in sim_db.query(SimCreator).all()
    }
    creator_ids = set()
    category_rollups = {}

    for comment, content in comment_rows:
        intent_label, demand_points, is_high_intent = score_comment_text(comment.text)
        comment.intent_label = intent_label
        category = (
            content.category
            or creators[content.creator_id].niche
            or "general"
        ).strip()
        signal = signal_by_comment_id.get(comment.id)
        if signal is None:
            signal = AudienceCommentSignal(sim_comment_id=comment.id)
            core_db.add(signal)
            signal_by_comment_id[comment.id] = signal

        signal.sim_post_id = content.id
        signal.sim_creator_id = content.creator_id
        signal.category = category
        signal.author_handle = comment.author_handle
        signal.comment_text = comment.text
        signal.intent_label = intent_label
        signal.demand_points = demand_points
        signal.is_high_intent = is_high_intent
        creator_ids.add(content.creator_id)

    for creator_id in creator_ids:
        metrics = compute_creator_demand_metrics(sim_db, creator_id)
        if metrics:
            _upsert_creator_snapshot(core_db, metrics)

    core_db.flush()
    categories = {
        signal.category
        for signal in signal_by_comment_id.values()
        if signal.category
    }
    category_snapshots_updated = 0
    for category in categories:
        signals = (
            core_db.query(AudienceCommentSignal)
            .filter(AudienceCommentSignal.category == category)
            .all()
        )
        high_intent_comments = sum(signal.is_high_intent for signal in signals)
        snapshot = (
            core_db.query(DemandSnapshot)
            .filter(
                DemandSnapshot.scope_type == "category",
                DemandSnapshot.scope_key == category.lower(),
            )
            .first()
        )
        if snapshot is None:
            snapshot = DemandSnapshot(
                scope_type="category",
                scope_key=category.lower(),
                category=category,
            )
            core_db.add(snapshot)

        snapshot.category = category
        snapshot.total_comments = len(signals)
        snapshot.high_intent_comments = high_intent_comments
        snapshot.demand_score = round(
            min(
                100.0,
                sum(signal.demand_points for signal in signals) * 2.5
                + high_intent_comments * 5.0,
            ),
            2,
        )
        snapshot.updated_at = datetime.utcnow()
        category_snapshots_updated += 1

    sim_db.commit()
    core_db.commit()
    return {
        "synced_comments": len(comment_rows),
        "creator_snapshots_updated": len(creator_ids),
        "category_snapshots_updated": category_snapshots_updated,
    }


@router.post("/creators/recompute-scores")
def recompute_creator_scores(
    sim_db: Session = Depends(get_sim_db),
    core_db: Session = Depends(get_core_db),
):
    creators = sim_db.query(SimCreator).order_by(SimCreator.id.asc()).all()
    updated = 0
    for creator in creators:
        if sync_creator_promotion_listing(sim_db, core_db, creator.id):
            updated += 1

    sim_db.commit()
    core_db.commit()
    return {"creators_updated": updated}
