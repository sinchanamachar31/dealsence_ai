from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from backend.database.core_db import CoreBase


class Enterprise(CoreBase):
    __tablename__ = "enterprises"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(120), nullable=False, index=True)
    industry = Column(String(80), nullable=False, index=True)
    target_categories = Column(String(255), nullable=False, default="beauty,fitness,food,home,tech")
    monthly_budget = Column(Float, nullable=False, default=50000.0)
    contact_email = Column(String(150), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    promotions = relationship("DealPromotion", back_populates="enterprise", cascade="all, delete-orphan")
    listings = relationship("CreatorPromotionListing", back_populates="enterprise", cascade="all, delete-orphan")


class DealPromotion(CoreBase):
    __tablename__ = "deals_promotions"

    id = Column(Integer, primary_key=True, index=True)
    enterprise_id = Column(Integer, ForeignKey("enterprises.id"), nullable=False, index=True)
    title = Column(String(180), nullable=False)
    product_name = Column(String(180), nullable=False)
    category = Column(String(80), nullable=False, index=True)
    compensation_model = Column(String(40), nullable=False, default="hybrid")
    flat_fee = Column(Float, nullable=False, default=0.0)
    commission_pct = Column(Float, nullable=False, default=10.0)
    min_demand_score = Column(Float, nullable=False, default=0.0)
    status = Column(String(30), nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    enterprise = relationship("Enterprise", back_populates="promotions")
    listings = relationship("CreatorPromotionListing", back_populates="promotion")


class AudienceCommentSignal(CoreBase):
    __tablename__ = "audience_comment_signals"

    id = Column(Integer, primary_key=True, index=True)
    sim_comment_id = Column(Integer, nullable=True, index=True)
    sim_post_id = Column(Integer, nullable=False, index=True)
    sim_creator_id = Column(Integer, nullable=False, index=True)
    category = Column(String(80), nullable=False, index=True)
    author_handle = Column(String(100), nullable=True)
    comment_text = Column(Text, nullable=False)
    intent_label = Column(String(40), nullable=False, default="general")
    demand_points = Column(Float, nullable=False, default=1.0)
    is_high_intent = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DemandSnapshot(CoreBase):
    __tablename__ = "demand_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    scope_type = Column(String(30), nullable=False, index=True)
    scope_key = Column(String(120), nullable=False, index=True)
    category = Column(String(80), nullable=False, index=True)
    total_comments = Column(Integer, nullable=False, default=0)
    high_intent_comments = Column(Integer, nullable=False, default=0)
    demand_score = Column(Float, nullable=False, default=0.0)
    engagement_rate = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CreatorPromotionListing(CoreBase):
    __tablename__ = "creator_promotion_listings"

    id = Column(Integer, primary_key=True, index=True)
    sim_creator_id = Column(Integer, nullable=False, unique=True, index=True)
    creator_handle = Column(String(120), nullable=False, index=True)
    creator_name = Column(String(150), nullable=False)
    niche = Column(String(80), nullable=False, index=True)
    followers = Column(Integer, nullable=False, default=0)
    engagement_rate = Column(Float, nullable=False, default=0.0)
    total_comments_tracked = Column(Integer, nullable=False, default=0)
    high_intent_comments = Column(Integer, nullable=False, default=0)
    audience_demand_score = Column(Float, nullable=False, default=0.0)
    promotion_fit_score = Column(Float, nullable=False, default=0.0)
    recommended_fee = Column(Float, nullable=False, default=0.0)
    available_for_promo = Column(Boolean, nullable=False, default=True)
    promotion_status = Column(String(40), nullable=False, default="available")
    enterprise_id = Column(Integer, ForeignKey("enterprises.id"), nullable=True, index=True)
    promotion_id = Column(Integer, ForeignKey("deals_promotions.id"), nullable=True, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    enterprise = relationship("Enterprise", back_populates="listings")
    promotion = relationship("DealPromotion", back_populates="listings")
