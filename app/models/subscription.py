from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.sql import func
from app.core.database import Base


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Ownership
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    # Status
    status = Column(
        String(30),
        default="active",
        index=True
    )
    # active, trialing, past_due, canceled, expired

    # Billing Period
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)

    # Billing Provider (Stripe)
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)

    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        # One active subscription per tenant
        UniqueConstraint("tenant_id", "status", name="uq_tenant_active_subscription"),
        Index("idx_subscription_tenant_status", "tenant_id", "status"),
    )
