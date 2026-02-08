from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..auth import auth
from ..models.models import Project, UserModel
from ..schemas.Project import (
    AddUserToProject,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
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
            username=current_user.username,
            email=current_user.email,
        )
        db.add(db_user)

    new_project = Project(title=project_data.title)
    new_project.users.append(db_user)

    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    # Eagerly load the users relationship before returning
    await db.refresh(new_project, ["users"])

    return new_project


@router.get("/", response_model=List[ProjectResponse])
async def get_my_projects(
    current_user: UserModel = Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Project)
        .options(selectinload(Project.users))
        .join(Project.users)
        .where(UserModel.id == current_user.user_id)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_by_id(
    project_id: int,
    current_user: UserModel = Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Project)
        .options(selectinload(Project.users))
        .join(Project.users)
        .where(UserModel.id == current_user.user_id, Project.id == project_id)
    )
    result = await db.execute(query)
    project = result.scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    return project


@router.post("/{project_id}/users", response_model=ProjectResponse)
async def add_user_to_project(
    project_id: int,
    user_data: AddUserToProject,
    current_user: UserModel = Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a user to a project. Only project members can add other users."""
    query = (
        select(Project)
        .options(selectinload(Project.users))
        .join(Project.users)
        .where(Project.id == project_id, UserModel.id == current_user.user_id)
    )
    result = await db.execute(query)
    project = result.scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    user_result = await db.execute(
        select(UserModel).where(UserModel.id == user_data.user_id)
    )
    user_to_add = user_result.scalars().first()

    if not user_to_add:
        raise HTTPException(status_code=404, detail="User not found")

    if user_to_add in project.users:
        raise HTTPException(status_code=400, detail="User already in project")

    project.users.append(user_to_add)
    await db.commit()

    await db.refresh(project, ["users"])

    return project


@router.delete("/{project_id}/users/{user_id}", response_model=ProjectResponse)
async def remove_user_from_project(
    project_id: int,
    user_id: str,
    current_user: UserModel = Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a user from a project. Only project members can remove users."""
    query = (
        select(Project)
        .options(selectinload(Project.users))
        .join(Project.users)
        .where(Project.id == project_id, UserModel.id == current_user.user_id)
    )
    result = await db.execute(query)
    project = result.scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    user_to_remove = next((u for u in project.users if u.id == user_id), None)

    if not user_to_remove:
        raise HTTPException(status_code=404, detail="User not in project")

    if len(project.users) == 1:
        raise HTTPException(
            status_code=400, detail="Cannot remove last user from project"
        )

    project.users.remove(user_to_remove)
    await db.commit()

    await db.refresh(project, ["users"])

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: UserModel = Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Project)
        .options(selectinload(Project.users))
        .join(Project.users)
        .where(Project.id == project_id, UserModel.id == current_user.user_id)
    )
    result = await db.execute(query)
    project = result.scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    if project_data.title:
        project.title = project_data.title

    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: UserModel = Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Project)
        .join(Project.users)
        .where(Project.id == project_id, UserModel.id == current_user.user_id)
    )
    result = await db.execute(query)
    project = result.scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    await db.delete(project)
    await db.commit()
    return {"message": "Project deleted"}
