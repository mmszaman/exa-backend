"""
Chat API endpoints for SMBPilot AI Agent.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.clerk_auth import get_current_user, CurrentUser
from app.core.logger import get_logger

from app.schemas.conversation_schema import (
    ChatRequest,
    ChatResponse,
    Conversation,
    ConversationWithMessages,
    Message,
)
from app.services.conversation_service import ConversationService, MessageService
from app.services.ai_service import SMBPilotAgent
from app.services.tenant_service import TenantService
from app.services.membership_service import MembershipService

# Import tools
from app.services.ai_tools.business_tools import (
    create_business,
    list_businesses,
    get_business,
    update_business,
    delete_business,
)
from app.services.ai_tools.tenant_tools import (
    list_tenants,
    get_current_tenant,
    set_primary_tenant,
    get_tenant_info,
)
from app.services.ai_tools.tool_wrappers import (
    create_business_wrapper,
    list_businesses_wrapper,
    get_business_wrapper,
    update_business_wrapper,
    delete_business_wrapper,
    list_tenants_wrapper,
    get_current_tenant_wrapper,
    set_primary_tenant_wrapper,
    get_tenant_info_wrapper,
)

logger = get_logger("chat_api")
router = APIRouter()

# Initialize the AI agent (singleton)
agent = SMBPilotAgent()

# Map of wrapper names to actual functions
TOOL_IMPLEMENTATIONS = {
    "create_business_wrapper": create_business,
    "list_businesses_wrapper": list_businesses,
    "get_business_wrapper": get_business,
    "update_business_wrapper": update_business,
    "delete_business_wrapper": delete_business,
    "list_tenants_wrapper": list_tenants,
    "get_current_tenant_wrapper": get_current_tenant,
    "set_primary_tenant_wrapper": set_primary_tenant,
    "get_tenant_info_wrapper": get_tenant_info,
}

# Define wrapper tools (only user-facing parameters)
BASE_TOOLS = [
    create_business_wrapper,
    list_businesses_wrapper,
    get_business_wrapper,
    update_business_wrapper,
    delete_business_wrapper,
    list_tenants_wrapper,
    get_current_tenant_wrapper,
    set_primary_tenant_wrapper,
    get_tenant_info_wrapper,
]


@router.post("", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to SMBPilot AI agent.
    
    If conversation_id is provided, continues existing conversation.
    Otherwise, creates a new conversation.
    """
    try:
        # Determine tenant_id (from request or user's primary tenant)
        tenant_id = chat_request.tenant_id
        
        if not tenant_id:
            # Get user's primary tenant
            memberships = await MembershipService.get_user_memberships(
                db=db,
                user_id=current_user.id,
                active_only=True
            )
            
            if memberships:
                # Sort by primary
                memberships.sort(key=lambda m: (not m.is_primary, m.created_at))
                tenant_id = memberships[0].tenant_id
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No active tenant found. Please create or join an organization first."
                )
        
        # Get or create conversation
        if chat_request.conversation_id:
            conversation = await ConversationService.get_conversation(
                db=db,
                conversation_id=chat_request.conversation_id,
                user_id=current_user.id
            )
            
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation = await ConversationService.create_conversation(
                db=db,
                user_id=current_user.id,
                tenant_id=tenant_id
            )
        
        # Get conversation history
        messages = await MessageService.get_recent_messages(
            db=db,
            conversation_id=conversation.id,
            limit=20  # Last 20 messages for context
        )
        
        # Convert to dict format for agent
        conversation_history = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
        
        # Get user and tenant info for context
        user_info = {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
        }
        
        tenant = await TenantService.get_tenant_by_id(db, tenant_id)
        membership = await MembershipService.get_membership(db, current_user.id, tenant_id)
        
        tenant_info = {
            "id": tenant_id,
            "name": tenant.name if tenant else "Unknown",
            "role": membership.role if membership else "member",
        }
        
        # Save user message
        user_message = await MessageService.create_message(
            db=db,
            conversation_id=conversation.id,
            role="user",
            content=chat_request.message
        )
        
        # Build graph with wrapper tools and implementation mapping
        agent.build_graph(BASE_TOOLS, TOOL_IMPLEMENTATIONS)
        
        # Call the AI agent
        agent_response = await agent.chat(
            message=chat_request.message,
            user_id=current_user.id,
            tenant_id=tenant_id,
            user_info=user_info,
            tenant_info=tenant_info,
            conversation_history=conversation_history,
            db=db
        )
        
        # Save assistant message
        assistant_message = await MessageService.create_message(
            db=db,
            conversation_id=conversation.id,
            role="assistant",
            content=agent_response["response"],
            extra_metadata={
                "success": agent_response.get("success", True),
                "error": agent_response.get("error")
            }
        )
        
        # Convert to response schema
        message_response = Message(
            id=assistant_message.id,
            conversation_id=conversation.id,
            role=assistant_message.role,
            content=assistant_message.content,
            function_call=assistant_message.function_call,
            function_response=assistant_message.function_response,
            extra_metadata=assistant_message.extra_metadata,
            created_at=assistant_message.created_at
        )
        
        return ChatResponse(
            conversation_id=conversation.id,
            message=message_response,
            suggestions=None  # TODO: Generate suggestions based on context
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your message: {str(e)}"
        )


@router.get("/conversations", response_model=List[Conversation])
async def get_conversations(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    tenant_id: Optional[int] = None,
    limit: int = 50,
    skip: int = 0
):
    """
    Get all conversations for the current user.
    
    Optionally filter by tenant_id.
    """
    conversations = await ConversationService.get_user_conversations(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id,
        limit=limit,
        skip=skip
    )
    
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific conversation with all messages.
    """
    conversation = await ConversationService.get_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    messages = await MessageService.get_conversation_messages(
        db=db,
        conversation_id=conversation_id
    )
    
    # Convert to schema
    return ConversationWithMessages(
        id=conversation.id,
        user_id=conversation.user_id,
        tenant_id=conversation.tenant_id,
        title=conversation.title,
        status=conversation.status,
        context=conversation.context,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        archived_at=conversation.archived_at,
        messages=[
            Message(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                function_call=msg.function_call,
                function_response=msg.function_response,
                extra_metadata=msg.extra_metadata,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation (soft delete).
    """
    success = await ConversationService.delete_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return None
