"""
Pydantic schemas for request/response validation.
Schemas define the API contract and data types.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class NotifyEmailRequest(BaseModel):
    """Request body for /notify-email endpoint"""

    email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {"email": "user@example.com"}
        }


class NotifyEmailResponse(BaseModel):
    """Response body for /notify-email endpoint"""

    success: bool
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Email notification request received",
            }
        }


class HealthResponse(BaseModel):
    """Response body for /health endpoint"""

    status: str
    time: str

    class Config:
        json_schema_extra = {
            "example": {"status": "ok", "time": "2025-11-27T12:34:56.000000"}
        }
