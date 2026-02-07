from pydantic import BaseModel
from typing import List, Optional
from .User import UserResponse


class ProjectBase(BaseModel):
    title: str


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None


class AddUserToProject(BaseModel):
    user_id: str


class ProjectResponse(ProjectBase):
    id: int
    users: List[UserResponse] = []

    model_config = {"from_attributes": True}
