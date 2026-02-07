from pydantic import BaseModel
from typing import List, Optional


class ProjectBase(BaseModel):
    title: str


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int

    class Config:
        from_attributes = True
