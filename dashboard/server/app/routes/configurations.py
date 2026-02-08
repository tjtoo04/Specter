from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..auth import auth
from ..database import get_db
from ..models.models import ConfigRequest, Configuration, Project
from ..schemas.Configuration import (
    ConfigurationCreate,
    ConfigurationResponse,
    ConfigurationUpdate,
)

router = APIRouter(prefix="/api/configs", tags=["configurations"])


@router.post("/{project_id}", response_model=ConfigurationResponse)
async def create_config(
    project_id: int,
    config_in: ConfigurationCreate,
    current_user=Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    new_config = Configuration(
        **config_in.model_dump(),
        user_id=current_user.user_id,
        project_id=project_id,
    )
    db.add(new_config)
    await db.commit()
    stmt = (
        select(Configuration)
        .where(Configuration.id == new_config.id)
        .options(
            selectinload(Configuration.user),
            selectinload(Configuration.project).selectinload(Project.users),
        )
    )

    result = await db.execute(stmt)
    db_config = result.scalars().first()

    return db_config


@router.post("/project/{project_id}", response_model=List[ConfigurationResponse])
async def get_project_configs_cli(
    project_id: int,
    request_data: ConfigRequest,
    current_user=Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Configuration)
        .where(
            Configuration.project_id == project_id,
            Configuration.user_id == request_data.user_id,
        )
        .options(
            selectinload(Configuration.user),
            selectinload(Configuration.project).selectinload(Project.users),
        )
    )

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/project/{project_id}", response_model=List[ConfigurationResponse])
async def get_project_configs(
    project_id: int,
    current_user=Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):

    print(current_user.user_id, project_id)
    stmt = (
        select(Configuration)
        .where(
            Configuration.project_id == project_id,
            Configuration.user_id == current_user.user_id,
        )
        .options(
            selectinload(Configuration.user),
            selectinload(Configuration.project).selectinload(Project.users),
        )
    )

    result = await db.execute(stmt)
    return result.scalars().all()


@router.patch("/{config_id}", response_model=ConfigurationResponse)
async def update_config(
    config_id: int,
    config_update: ConfigurationUpdate,
    current_user=Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Configuration).where(Configuration.id == config_id)
    )
    db_config = result.scalars().first()

    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    if db_config.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to edit this config"
        )

    update_data = config_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_config, key, value)

    await db.commit()
    stmt = (
        select(Configuration)
        .where(Configuration.id == config_id)
        .options(
            selectinload(Configuration.user),
            selectinload(Configuration.project).selectinload(Project.users),
        )
    )

    final_result = await db.execute(stmt)
    return final_result.scalars().first()


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    config_id: int,
    current_user=Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Configuration).where(Configuration.id == config_id)
    )
    db_config = result.scalars().first()

    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    if db_config.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this config"
        )

    await db.delete(db_config)
    await db.commit()
    return None
