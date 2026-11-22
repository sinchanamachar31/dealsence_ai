from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.sim_db import get_sim_db
from backend.database.core_db import get_core_db
from backend.models.sim_models import SimActivityLog, SimCreator
from backend.models.core_models import (
    CreatorPromotionListing,
    DealPromotion,
    Enterprise,
)
from backend.api.internal_bridge import sync_creator_promotion_listing

router = APIRouter(prefix="/api/enterprise", tags=["Enterprise & Promotions"])


class EnterpriseCreate(BaseModel):
    company_name: str = Field(min_length=1, max_length=120)
    industry: str = Field(min_length=1, max_length=80)
    target_categories: str = Field(default="Healthy Food & Nutrition,Clean Skincare & Beauty,Home Fitness & Strength")
    monthly_budget: float = Field(default=50000.0, ge=0)
    contact_email: Optional[str] = None


class PromotionCreate(BaseModel):
    enterprise_id: int
    title: str = Field(min_length=1, max_length=180)
    product_name: str = Field(min_length=1, max_length=180)
    category: str = Field(min_length=1, max_length=80)
    compensation_model: str = Field(default="hybrid")
    flat_fee: float = Field(default=2500.0, ge=0)
    commission_pct: float = Field(default=12.0, ge=0, le=100)
    min_demand_score: float = Field(default=0.0, ge=0, le=100)
    status: str = Field(default="active")


class AssignPromotionRequest(BaseModel):
    enterprise_id: int
    promotion_id: Optional[int] = None
    agreed_fee: Optional[float] = Field(default=None, ge=0)
    promotion_status: str = Field(default="assigned")


def _ensure_starter_enterprise(core_db: Session) -> Enterprise:
    existing = core_db.query(Enterprise).order_by(Enterprise.id.asc()).first()
    if existing:
        return existing
    starter = Enterprise(
        company_name="DealSense Partner Brands",
        industry="Consumer & Lifestyle",
        target_categories="Healthy Food & Nutrition,Clean Skincare & Beauty,Home Fitness & Strength,Tech & Student Productivity,Sustainable Home & Decor",
        monthly_budget=150000.0,
        contact_email="partnerships@dealsense.demo",
    )
    core_db.add(starter)
    core_db.commit()
    core_db.refresh(starter)
    return starter


def _ensure_listings_populated(sim_db: Session, core_db: Session) -> None:
    if core_db.query(CreatorPromotionListing).count() > 0:
        return
    creators = sim_db.query(SimCreator).order_by(SimCreator.id.asc()).all()
    for creator in creators:
        sync_creator_promotion_listing(sim_db, core_db, creator.id)
    sim_db.commit()
    core_db.commit()


def _listing_payload(item: CreatorPromotionListing) -> dict:
    return {
        "id": item.id,
        "sim_creator_id": item.sim_creator_id,
        "creator_handle": item.creator_handle,
        "creator_name": item.creator_name,
        "niche": item.niche,
        "followers": item.followers,
        "engagement_rate": item.engagement_rate,
        "total_comments_tracked": item.total_comments_tracked,
        "high_intent_comments": item.high_intent_comments,
        "audience_demand_score": item.audience_demand_score,
        "promotion_fit_score": item.promotion_fit_score,
        "recommended_fee": item.recommended_fee,
        "available_for_promo": item.available_for_promo,
        "promotion_status": item.promotion_status,
        "enterprise_id": item.enterprise_id,
        "promotion_id": item.promotion_id,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
    }


@router.get("/enterprises")
def list_enterprises(core_db: Session = Depends(get_core_db)):
    _ensure_starter_enterprise(core_db)
    enterprises = core_db.query(Enterprise).order_by(Enterprise.id.asc()).all()
    return [
        {
            "id": e.id,
            "company_name": e.company_name,
            "industry": e.industry,
            "target_categories": e.target_categories,
            "monthly_budget": e.monthly_budget,
            "contact_email": e.contact_email,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in enterprises
    ]


@router.post("/enterprises")
def create_enterprise(payload: EnterpriseCreate, core_db: Session = Depends(get_core_db)):
    enterprise = Enterprise(
        company_name=payload.company_name.strip(),
        industry=payload.industry.strip(),
        target_categories=payload.target_categories.strip(),
        monthly_budget=payload.monthly_budget,
        contact_email=payload.contact_email.strip() if payload.contact_email else None,
    )
    core_db.add(enterprise)
    core_db.commit()
    core_db.refresh(enterprise)
    return {
        "id": enterprise.id,
        "company_name": enterprise.company_name,
        "industry": enterprise.industry,
        "target_categories": enterprise.target_categories,
        "monthly_budget": enterprise.monthly_budget,
        "contact_email": enterprise.contact_email,
    }


@router.get("/promotions")
def list_promotions(
    enterprise_id: Optional[int] = Query(default=None),
    category: Optional[str] = Query(default=None),
    core_db: Session = Depends(get_core_db),
):
    _ensure_starter_enterprise(core_db)
    query = core_db.query(DealPromotion)
    if enterprise_id is not None:
        query = query.filter(DealPromotion.enterprise_id == enterprise_id)
    if category:
        query = query.filter(DealPromotion.category.ilike(f"%{category.strip()}%"))
    promos = query.order_by(DealPromotion.id.desc()).all()
    return [
        {
            "id": p.id,
            "enterprise_id": p.enterprise_id,
            "title": p.title,
            "product_name": p.product_name,
            "category": p.category,
            "compensation_model": p.compensation_model,
            "flat_fee": p.flat_fee,
            "commission_pct": p.commission_pct,
            "min_demand_score": p.min_demand_score,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in promos
    ]


@router.post("/promotions")
def create_promotion(payload: PromotionCreate, core_db: Session = Depends(get_core_db)):
    enterprise = core_db.query(Enterprise).filter(Enterprise.id == payload.enterprise_id).first()
    if not enterprise:
        raise HTTPException(status_code=404, detail="Enterprise not found")

    promo = DealPromotion(
        enterprise_id=payload.enterprise_id,
        title=payload.title.strip(),
        product_name=payload.product_name.strip(),
        category=payload.category.strip(),
        compensation_model=payload.compensation_model.strip(),
        flat_fee=payload.flat_fee,
        commission_pct=payload.commission_pct,
        min_demand_score=payload.min_demand_score,
        status=payload.status.strip(),
    )
    core_db.add(promo)
    core_db.commit()
    core_db.refresh(promo)
    return {
        "id": promo.id,
        "enterprise_id": promo.enterprise_id,
        "title": promo.title,
        "product_name": promo.product_name,
        "category": promo.category,
        "compensation_model": promo.compensation_model,
        "flat_fee": promo.flat_fee,
        "commission_pct": promo.commission_pct,
        "min_demand_score": promo.min_demand_score,
        "status": promo.status,
    }


@router.get("/creators")
def list_enterprise_creators(
    niche: Optional[str] = Query(default=None),
    min_demand_score: float = Query(default=0.0, ge=0),
    available_only: bool = Query(default=False),
    promotion_status: Optional[str] = Query(default=None),
    sort_by: str = Query(default="promotion_fit_score"),
    limit: int = Query(default=50, ge=1, le=200),
    sim_db: Session = Depends(get_sim_db),
    core_db: Session = Depends(get_core_db),
):
    _ensure_listings_populated(sim_db, core_db)

    query = core_db.query(CreatorPromotionListing).filter(
        CreatorPromotionListing.audience_demand_score >= min_demand_score
    )
    if niche and niche.strip():
        query = query.filter(CreatorPromotionListing.niche.ilike(f"%{niche.strip()}%"))
    if available_only:
        query = query.filter(CreatorPromotionListing.available_for_promo.is_(True))
    if promotion_status and promotion_status.strip():
        query = query.filter(CreatorPromotionListing.promotion_status == promotion_status.strip())

    sort_col = {
        "promotion_fit_score": CreatorPromotionListing.promotion_fit_score,
        "audience_demand_score": CreatorPromotionListing.audience_demand_score,
        "follower_count": CreatorPromotionListing.followers,
        "engagement_rate": CreatorPromotionListing.engagement_rate,
    }.get(sort_by, CreatorPromotionListing.promotion_fit_score)

    items = query.order_by(sort_col.desc(), CreatorPromotionListing.id.asc()).limit(limit).all()
    return [_listing_payload(item) for item in items]


@router.post("/creators/{sim_creator_id}/assign-promotion")
def assign_creator_promotion(
    sim_creator_id: int,
    payload: AssignPromotionRequest,
    sim_db: Session = Depends(get_sim_db),
    core_db: Session = Depends(get_core_db),
):
    _ensure_listings_populated(sim_db, core_db)

    enterprise = core_db.query(Enterprise).filter(Enterprise.id == payload.enterprise_id).first()
    if not enterprise:
        raise HTTPException(status_code=404, detail="Enterprise not found")

    if payload.promotion_id is not None:
        promo = core_db.query(DealPromotion).filter(DealPromotion.id == payload.promotion_id).first()
        if not promo:
            raise HTTPException(status_code=404, detail="Promotion not found")

    listing = (
        core_db.query(CreatorPromotionListing)
        .filter(CreatorPromotionListing.sim_creator_id == sim_creator_id)
        .first()
    )
    if not listing:
        raise HTTPException(status_code=404, detail="Creator promotion listing not found")

    listing.enterprise_id = payload.enterprise_id
    listing.promotion_id = payload.promotion_id
    listing.promotion_status = payload.promotion_status.strip() or "assigned"
    listing.available_for_promo = listing.promotion_status == "available"
    if payload.agreed_fee is not None:
        listing.recommended_fee = payload.agreed_fee
    listing.updated_at = datetime.utcnow()

    sim_db.add(
        SimActivityLog(
            creator_id=sim_creator_id,
            event_type="promotion_assigned",
            description=f"{enterprise.company_name} assigned promotion to {listing.creator_handle} ({listing.promotion_status})",
        )
    )
    sim_db.commit()
    core_db.commit()
    core_db.refresh(listing)

    return {
        "message": "Creator promotion updated",
        "listing": _listing_payload(listing),
    }
