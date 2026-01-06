from sqlalchemy import Column, BigInteger, Numeric, String, Boolean, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class ProductModel(Base):
    __tablename__ = "products"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True, nullable=False)

    # Ownership & Relationships
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"), nullable=False, index=True)
    business_id = Column(BigInteger, ForeignKey("businesses.id"), nullable=True, index=True)
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)

    # Identity
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    type = Column(String(50), nullable=False, index=True)  # e.g., 'plan', 'service', 'product'
    
    # Versioning
    version = Column(BigInteger, nullable=False, default=1)
    is_current = Column(Boolean, default=True, index=True)

    # Pricing
    price_monthly = Column(Numeric(10, 2), nullable=True)
    price_yearly = Column(Numeric(10, 2), nullable=True)
    price_fixed = Column(Numeric(10, 2), nullable=True)  # For one-time payment services
    currency = Column(String(10), default="USD")

    # Features & Limits
    features = Column(JSONB, nullable=True)
    limits = Column(JSONB, nullable=True)

    # Billing Integration
    stripe_product_id = Column(String(255), unique=True, nullable=True)
    stripe_price_monthly_id = Column(String(255), nullable=True)
    stripe_price_yearly_id = Column(String(255), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_public = Column(Boolean, default=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    __table_args__ = (
        Index("idx_product_code_version", "code", "version"),
        Index("idx_product_active_current", "is_active", "is_current"),
    )
