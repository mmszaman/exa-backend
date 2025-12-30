from fastapi import APIRouter, Depends, HTTPException, status, Request, Header, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json
import asyncio
from svix.webhooks import Webhook, WebhookVerificationError
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.config import settings
from app.core.logger import get_logger
from app.services.user_service import UserService
from app.services.session_service import SessionService

logger = get_logger("clerk_webhooks")
router = APIRouter()


#################################################
# GET /webhook/clerk - Health check
@router.get("/clerk", status_code=status.HTTP_200_OK)
async def webhook_health_check():
    """Health check endpoint for webhook"""
    return {
        "status": "ok",
        "message": "Clerk webhook endpoint is ready",
        "method": "POST"
    }


#################################################
# POST /webhook/clerk
# Handle Clerk webhook events for user synchronization
@router.post("/clerk", status_code=status.HTTP_200_OK)
async def handle_clerk_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    svix_id: Optional[str] = Header(None, alias="svix-id"),
    svix_timestamp: Optional[str] = Header(None, alias="svix-timestamp"),
    svix_signature: Optional[str] = Header(None, alias="svix-signature"),
):  
    logger.info("===== CLERK WEBHOOK RECEIVED =====")
    logger.info(f"Headers - svix-id: {svix_id}, svix-timestamp: {svix_timestamp}")
    
    # Get the raw body for signature verification
    body = await request.body()
    body_str = body.decode('utf-8')
    logger.info(f"Webhook body: {body_str[:500]}...")  # Log first 500 chars
    
    # Verify webhook signature
    if not settings.CLERK_WEBHOOK_SECRET:
        logger.error("CLERK_WEBHOOK_SECRET not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured"
        )
    
    # Verify the webhook signature
    try:
        wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
        payload = wh.verify(body, {
            "svix-id": svix_id,
            "svix-timestamp": svix_timestamp,
            "svix-signature": svix_signature,
        })
        logger.info("✓ Webhook signature verified successfully")
        logger.info(f"Event type: {payload.get('type')}")
    except WebhookVerificationError as e:
        logger.error(f"✗ Webhook verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
    except Exception as e:
        logger.error(f"✗ Webhook processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook error: {str(e)}"
        )
    
    # Parse the event
    event_type = payload.get("type")
    event_data = payload.get("data", {})
    
    logger.info(f"Processing Clerk webhook: {event_type}")
    
    try:
        if event_type == "user.created":
            # Extract user data from Clerk webhook
            clerk_user_id = event_data.get("id")
            email_addresses = event_data.get("email_addresses", [])
            primary_email = None
            
            # Find primary email
            for email_obj in email_addresses:
                if email_obj.get("id") == event_data.get("primary_email_address_id"):
                    primary_email = email_obj.get("email_address")
                    break
            
            if not primary_email and email_addresses:
                primary_email = email_addresses[0].get("email_address")
            
            username = event_data.get("username")
            first_name = event_data.get("first_name", "")
            last_name = event_data.get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            avatar_url = event_data.get("profile_image_url") or event_data.get("image_url")
            
            # Extract phone number
            phone_numbers = event_data.get("phone_numbers", [])
            primary_phone = None
            if phone_numbers:
                for phone_obj in phone_numbers:
                    if phone_obj.get("id") == event_data.get("primary_phone_number_id"):
                        primary_phone = phone_obj.get("phone_number")
                        break
                if not primary_phone:
                    primary_phone = phone_numbers[0].get("phone_number")
            
            # Extract metadata
            public_metadata = event_data.get("public_metadata", {})
            private_metadata = event_data.get("private_metadata", {})
            unsafe_metadata = event_data.get("unsafe_metadata", {})
            
            # Extract marketing data from metadata
            lead_source = public_metadata.get("lead_source") or unsafe_metadata.get("lead_source")
            brand = public_metadata.get("brand") or unsafe_metadata.get("brand")
            referral_code = public_metadata.get("referral_code") or unsafe_metadata.get("referral_code")
            utm_source = unsafe_metadata.get("utm_source")
            utm_medium = unsafe_metadata.get("utm_medium")
            utm_campaign = unsafe_metadata.get("utm_campaign")
            
            # Store all metadata as JSON
            clerk_metadata = json.dumps({
                "public": public_metadata,
                "private": private_metadata,
                "unsafe": unsafe_metadata
            })
            
            # Create user in local database
            await UserService.create_from_clerk(
                db=db,
                clerk_user_id=clerk_user_id,
                email=primary_email,
                username=username,
                full_name=full_name if full_name else None,
                avatar_url=avatar_url,
                phone_number=primary_phone,
                lead_source=lead_source,
                brand=brand,
                referral_code=referral_code,
                utm_source=utm_source,
                utm_medium=utm_medium,
                utm_campaign=utm_campaign,
                clerk_metadata=clerk_metadata
            )
            logger.info(f"Created user from Clerk: {clerk_user_id}")
        
        elif event_type == "user.updated":
            # Update user information
            clerk_user_id = event_data.get("id")
            email_addresses = event_data.get("email_addresses", [])
            primary_email = None
            
            for email_obj in email_addresses:
                if email_obj.get("id") == event_data.get("primary_email_address_id"):
                    primary_email = email_obj.get("email_address")
                    break
            
            username = event_data.get("username")
            first_name = event_data.get("first_name", "")
            last_name = event_data.get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            avatar_url = event_data.get("profile_image_url") or event_data.get("image_url")
            
            # Extract phone number
            phone_numbers = event_data.get("phone_numbers", [])
            primary_phone = None
            if phone_numbers:
                for phone_obj in phone_numbers:
                    if phone_obj.get("id") == event_data.get("primary_phone_number_id"):
                        primary_phone = phone_obj.get("phone_number")
                        break
                if not primary_phone:
                    primary_phone = phone_numbers[0].get("phone_number")
            
            # Extract metadata
            public_metadata = event_data.get("public_metadata", {})
            private_metadata = event_data.get("private_metadata", {})
            unsafe_metadata = event_data.get("unsafe_metadata", {})
            
            clerk_metadata = json.dumps({
                "public": public_metadata,
                "private": private_metadata,
                "unsafe": unsafe_metadata
            })
            
            await UserService.update_from_clerk(
                db=db,
                clerk_user_id=clerk_user_id,
                email=primary_email,
                username=username,
                full_name=full_name if full_name else None,
                avatar_url=avatar_url,
                phone_number=primary_phone,
                clerk_metadata=clerk_metadata
            )
            logger.info(f"Updated user from Clerk: {clerk_user_id}")
        
        elif event_type == "user.deleted":
            # Soft delete: deactivate user instead of hard delete
            clerk_user_id = event_data.get("id")
            try:
                await UserService.deactivate_user(db, clerk_user_id)
                logger.info(f"Deactivated user from Clerk: {clerk_user_id}")
            except HTTPException as e:
                if e.status_code == 404:
                    logger.warning(f"User {clerk_user_id} not found in database, may have been deleted already or never created")
                else:
                    raise
        
        elif event_type == "session.created":
            # Handle session creation
            clerk_session_id = event_data.get("id")
            clerk_user_id = event_data.get("user_id")
            clerk_org_id = event_data.get("active_organization_id")
            client_id = event_data.get("client_id")
            status_val = event_data.get("status", "active")
            
            # Extract session metadata (do this before user check)
            metadata = event_data.get("last_active_at") or event_data.get("metadata", {})
            clerk_metadata = json.dumps(metadata) if metadata else None
            
            # Convert expires_at timestamp (Clerk sends milliseconds)
            expires_at = event_data.get("expire_at")
            if expires_at:
                expires_at = datetime.fromtimestamp(expires_at / 1000, timezone.utc)
            
            # Get user from database
            user = await UserService.get_user_by_clerk_id(db, clerk_user_id)
            if user:
                await SessionService.create_or_update_session(
                    db=db,
                    clerk_session_id=clerk_session_id,
                    user_id=user.id,
                    clerk_user_id=clerk_user_id,
                    tenant_id=clerk_org_id,
                    status=status_val,
                    client_id=client_id,
                    expires_at=expires_at,
                    clerk_metadata=clerk_metadata
                )
                logger.info(f"Created session: {clerk_session_id} for user: {clerk_user_id}")
            else:
                logger.warning(f"User not found for session: {clerk_session_id}, user: {clerk_user_id}. Scheduling retry...")
                # Schedule background task to retry session creation
                background_tasks.add_task(
                    SessionService.retry_session_creation,
                    {
                        "clerk_session_id": clerk_session_id,
                        "clerk_user_id": clerk_user_id,
                        "tenant_id": clerk_org_id,
                        "status": status_val,
                        "client_id": client_id,
                        "expires_at": expires_at,
                        "clerk_metadata": clerk_metadata
                    }
                )
        
        elif event_type == "session.ended" or event_type == "session.removed" or event_type == "session.revoked":
            # Handle session end/removal/revocation
            clerk_session_id = event_data.get("id")
            await SessionService.end_session(db, clerk_session_id)
            logger.info(f"Ended session: {clerk_session_id}")
        
        else:
            logger.info(f"Unhandled webhook event: {event_type}")
    
    except Exception as e:
        logger.error(f"Error processing webhook {event_type}: {str(e)}", exc_info=True)
        # Raise exception so Clerk knows the webhook failed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing {event_type}: {str(e)}"
        )
    
    logger.info(f"✓ Successfully processed {event_type}")
    return {"success": True, "event": event_type}
