from typing import List

from fastapi import APIRouter, Depends, HTTPException
from propelauth_fastapi import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..auth import auth
from ..models.models import UserModel
from ..schemas.User import UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/whoami")
async def root(
    current_user: UserModel = Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserModel).where(UserModel.id == current_user.user_id)
    )
    db_user = result.scalars().first()

    if not db_user:
        db_user = UserModel(
            id=current_user.user_id,
            username=current_user.email,
            email=current_user.email,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

    return {
        "user_id": db_user.id,
        "email": db_user.email,
        "username": db_user.username,
        "internal_db": "synced",
    }


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"detail": "User deleted successfully"}


@router.get("/api/users/search", response_model=List[UserResponse])
async def search_users(
    q: str,
    current_user: User = Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    """Search for users by email or username"""
    if len(q) < 2:
        return []

    query = (
        select(UserModel)
        .where((UserModel.email.ilike(f"%{q}%")) | (UserModel.username.ilike(f"%{q}%")))
        .limit(10)
    )

    result = await db.execute(query)
    users = result.scalars().all()

    # Exclude current user from results
    return [user for user in users if user.id != current_user.user_id]
