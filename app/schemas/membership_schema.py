from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Membership(BaseModel):
    id: int
    user_id: int
    tenant_id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    joined_at: datetime
    
    class Config:
        from_attributes = True


class MembershipCreate(BaseModel):
    user_id: int
    tenant_id: int
    role: str = "member"
    is_active: bool = True


class MembershipUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
