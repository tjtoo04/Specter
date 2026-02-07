from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import Configuration
from ..schemas.Configuration import (
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationResponse,
)

from ..auth import auth

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
    await db.refresh(new_config, ["user", "project"])
    return new_config


@router.get("/project/{project_id}", response_model=List[ConfigurationResponse])
async def get_project_configs(
    project_id: int,
    current_user=Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Configuration).where(
            Configuration.project_id == project_id,
            Configuration.user_id == current_user.user_id,
        )
    )
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
    await db.refresh(db_config, ["user", "project"])
    return db_config


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_config(config_id: int, db: Session = Depends(get_db)):
    db_config = db.query(Configuration).filter(Configuration.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    db.delete(db_config)
    db.commit()
    return None
