from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from fastapi import HTTPException, status

from app.models.membership import MembershipModel


class MembershipService:

    # Create a new tenant membership
    @staticmethod
    async def create_membership(
        db: AsyncSession,
        user_id: int,
        tenant_id: int,
        role: str = "member",
        is_primary: bool = False
    ) -> MembershipModel:
        """Create a new tenant membership"""
        membership = MembershipModel(
            user_id=user_id,
            tenant_id=tenant_id,
            role=role,
            is_active=True,
            is_primary=is_primary
        )
        db.add(membership)
        await db.commit()
        await db.refresh(membership)
        return membership
    

    # Get a specific membership
    @staticmethod
    async def get_membership(
        db: AsyncSession,
        user_id: int,
        tenant_id: int
    ) -> Optional[MembershipModel]:
        """Get a specific membership by user_id and tenant_id"""
        stmt = select(MembershipModel).where(
            and_(
                MembershipModel.user_id == user_id,
                MembershipModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    

    # Get all memberships for a user
    @staticmethod
    async def get_user_memberships(
        db: AsyncSession,
        user_id: int,
        active_only: bool = True
    ) -> List[MembershipModel]:
        """Get all tenant memberships for a user"""
        stmt = select(MembershipModel).where(
            MembershipModel.user_id == user_id
        )
        
        if active_only:
            stmt = stmt.where(MembershipModel.is_active == True)
        
        stmt = stmt.options(selectinload(MembershipModel.tenant))
        result = await db.execute(stmt)
        return result.scalars().all()
    

    # Get all members of a tenant
    @staticmethod
    async def get_tenant_members(
        db: AsyncSession,
        tenant_id: int,
        active_only: bool = True
    ) -> List[MembershipModel]:
        """Get all members of a tenant"""
        stmt = select(MembershipModel).where(
            MembershipModel.tenant_id == tenant_id
        )
        
        if active_only:
            stmt = stmt.where(MembershipModel.is_active == True)
        
        stmt = stmt.options(selectinload(MembershipModel.user))
        result = await db.execute(stmt)
        return result.scalars().all()
    

    # Update a user's role in a tenant
    @staticmethod
    async def update_role(
        db: AsyncSession,
        user_id: int,
        tenant_id: int,
        new_role: str
    ) -> MembershipModel:
        """Update a user's role in a tenant"""
        membership = await MembershipService.get_membership(db, user_id, tenant_id)
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership not found"
            )
        
        membership.role = new_role
        await db.commit()
        await db.refresh(membership)
        return membership
    

    # Deactivate a membership
    @staticmethod
    async def deactivate_membership(
        db: AsyncSession,
        user_id: int,
        tenant_id: int
    ) -> MembershipModel:
        """Deactivate a membership (soft delete)"""
        membership = await MembershipService.get_membership(db, user_id, tenant_id)
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership not found"
            )
        
        membership.is_active = False
        await db.commit()
        await db.refresh(membership)
        return membership
    

    # Activate a membership
    @staticmethod
    async def activate_membership(
        db: AsyncSession,
        user_id: int,
        tenant_id: int
    ) -> MembershipModel:
        """Activate a membership"""
        membership = await MembershipService.get_membership(db, user_id, tenant_id)
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership not found"
            )
        
        membership.is_active = True
        await db.commit()
        await db.refresh(membership)
        return membership
    

    # Delete a membership
    @staticmethod
    async def delete_membership(
        db: AsyncSession,
        user_id: int,
        tenant_id: int
    ) -> None:
        """Hard delete a membership"""
        membership = await MembershipService.get_membership(db, user_id, tenant_id)
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership not found"
            )
        
        await db.delete(membership)
        await db.commit()
    

    # Check if a user has access to a tenant with optional role requirement
    @staticmethod
    async def check_user_access(
        db: AsyncSession,
        user_id: int,
        tenant_id: int,
        required_roles: Optional[List[str]] = None
    ) -> bool:
        """Check if a user has access to a tenant with optional role requirement"""
        membership = await MembershipService.get_membership(db, user_id, tenant_id)
        
        if not membership or not membership.is_active:
            return False
        
        if required_roles and membership.role not in required_roles:
            return False
        
        return True
    
    # Set primary tenant for a user
    @staticmethod
    async def set_primary_tenant(
        db: AsyncSession,
        user_id: int,
        tenant_id: int
    ) -> MembershipModel:
        """Set a tenant as the primary tenant for a user"""
        # Verify the membership exists and is active
        membership = await MembershipService.get_membership(db, user_id, tenant_id)
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership not found"
            )
        
        if not membership.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot set inactive membership as primary"
            )
        
        # Unset all other primary tenants for this user
        result = await db.execute(
            select(MembershipModel).filter(
                MembershipModel.user_id == user_id,
                MembershipModel.is_primary == True
            )
        )
        current_primary_memberships = result.scalars().all()
        
        for pm in current_primary_memberships:
            pm.is_primary = False
        
        # Set the new primary tenant
        membership.is_primary = True
        
        await db.commit()
        await db.refresh(membership)
        return membership
