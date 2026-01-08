from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


# ================== Billing Profile ==================

class BillingProfileModel(Base):
    __tablename__ = "billing_profiles"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True, nullable=False)

    # Ownership
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Provider
    provider = Column(String(50), nullable=False, default="stripe")  # stripe, paypal, etc.

    # Stripe Integration
    stripe_customer_id = Column(String(255), unique=True, nullable=True)

    # Billing Information
    billing_email = Column(String(255), nullable=True)
    billing_name = Column(String(255), nullable=True)
    billing_address = Column(JSONB, nullable=True)

    # Tax & Currency
    currency = Column(String(10), default="USD")
    tax_id = Column(String(100), nullable=True)
    tax_exempt = Column(Boolean, default=False)

    # Payment Methods
    default_payment_method = Column(String(255), nullable=True)
    payment_methods = Column(JSONB, nullable=True)

    # Provider Metadata
    provider_metadata = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)


# ================== Invoice ==================

class InvoiceStatus(str, enum.Enum):
    """Invoice status enumeration."""
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class InvoiceModel(Base):
    __tablename__ = "invoices"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True, nullable=False)

    # Ownership
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    billing_profile_id = Column(BigInteger, ForeignKey("billing_profiles.id"), nullable=True, index=True)
    subscription_id = Column(BigInteger, ForeignKey("subscriptions.id"), nullable=True, index=True)

    # Provider
    provider_invoice_id = Column(String(255), unique=True, nullable=True)

    # Status
    status = Column(SQLEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT, index=True)

    # Amounts
    currency = Column(String(10), default="USD")
    subtotal_amount = Column(Numeric(10, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)

    # Dates
    due_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # PDF
    invoice_pdf_url = Column(String(500), nullable=True)

    # Provider Metadata
    provider_metadata = Column(JSONB, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


# ================== Invoice Line Item ==================

class InvoiceLineItemModel(Base):
    __tablename__ = "invoice_line_items"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)

    # Ownership
    invoice_id = Column(BigInteger, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=True, index=True)

    # Line Item Details
    quantity = Column(BigInteger, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)

    # Metadata
    line_metadata = Column(JSONB, nullable=True)


# ================== Payment ==================

class PaymentStatus(str, enum.Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class PaymentModel(Base):
    __tablename__ = "payments"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True, nullable=False)

    # Ownership
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    billing_profile_id = Column(BigInteger, ForeignKey("billing_profiles.id"), nullable=True, index=True)
    invoice_id = Column(BigInteger, ForeignKey("invoices.id"), nullable=True, index=True)

    # Provider
    provider_payment_id = Column(String(255), unique=True, nullable=True)

    # Status
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, index=True)

    # Amount
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="USD")

    # Payment Method
    payment_method = Column(String(100), nullable=True)

    # Failure
    failure_reason = Column(Text, nullable=True)

    # Provider Metadata
    provider_metadata = Column(JSONB, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


# ================== Billing Credit ==================

class BillingCreditModel(Base):
    __tablename__ = "billing_credits"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)

    # Ownership
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    billing_profile_id = Column(BigInteger, ForeignKey("billing_profiles.id"), nullable=True, index=True)

    # Amount
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="USD")

    # Reason
    reason = Column(String(255), nullable=True)

    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


# ================== Usage Record ==================

class UsageRecordModel(Base):
    __tablename__ = "usage_records"

    # Primary Key
    id = Column(BigInteger, primary_key=True, index=True)

    # Ownership
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(BigInteger, ForeignKey("subscriptions.id"), nullable=True, index=True)

    # Metrics
    metric = Column(String(100), nullable=False, index=True)  # api_calls, storage_gb, users, etc.
    quantity = Column(BigInteger, nullable=False, default=0)

    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
