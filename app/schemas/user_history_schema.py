from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserHistory(BaseModel):
    id: int
    user_id: int
    clerk_user_id: str
    action: str
    description: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    action_metadata: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserHistoryCreate(BaseModel):
    user_id: int
    clerk_user_id: str
    action: str
    description: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    action_metadata: Optional[str] = None
