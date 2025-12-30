from sqlalchemy import JSON, Column, Integer, Numeric, String, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProductModel(Base):
    __tablename__ = "products"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Identity
    code = Column(String(50), unique=True, nullable=False, index=True)
    # e.g. free, starter, pro, enterprise

    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    # Pricing
    price_monthly = Column(Numeric(10, 2), nullable=True)
    price_yearly = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(10), default="USD")

    # Limits & Quotas
    max_users = Column(Integer, nullable=True)
    max_businesses = Column(Integer, nullable=True)
    max_projects = Column(Integer, nullable=True)

    # Feature Flags
    features = Column(JSON, nullable=True)
    # Example:
    # {
    #   "api_access": true,
    #   "advanced_reports": false,
    #   "priority_support": true
    # }

    # Billing Integration
    stripe_product_id = Column(String(255), unique=True, nullable=True)
    stripe_price_monthly_id = Column(String(255), nullable=True)
    stripe_price_yearly_id = Column(String(255), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_public = Column(Boolean, default=True)
    # is_public = visible in pricing page

    # Metadata
    product_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_product_active", "is_active"),
    )
