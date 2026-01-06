from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Message Schemas
class MessageBase(BaseModel):
    role: str = Field(..., description="Role: user, assistant, system, function")
    content: str = Field(..., description="Message content")
    function_call: Optional[Dict[str, Any]] = Field(None, description="Function call details")
    function_response: Optional[Dict[str, Any]] = Field(None, description="Function response")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MessageCreate(BaseModel):
    content: str = Field(..., description="Message content from user")


class Message(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# Conversation Schemas
class ConversationBase(BaseModel):
    title: Optional[str] = Field(None, description="Conversation title")
    tenant_id: Optional[int] = Field(None, description="Active tenant for this conversation")


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    tenant_id: Optional[int] = None


class Conversation(ConversationBase):
    id: int
    user_id: int
    status: str
    context: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ConversationWithMessages(Conversation):
    messages: List[Message] = []


# Chat Request/Response Schemas
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: Optional[int] = Field(None, description="Existing conversation ID")
    tenant_id: Optional[int] = Field(None, description="Active tenant context")
    stream: bool = Field(False, description="Enable streaming response")


class ChatResponse(BaseModel):
    conversation_id: int
    message: Message
    suggestions: Optional[List[str]] = Field(None, description="Suggested follow-up commands")


# Function Call Schemas
class FunctionParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: List[FunctionParameter]


class AvailableFunctions(BaseModel):
    functions: List[FunctionDefinition]
