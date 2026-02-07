from pydantic import BaseModel
from typing import List, Optional

from .Project import ProjectResponse
from .User import UserResponse


class ConfigurationBase(BaseModel):
    context: str


class ConfigurationCreate(ConfigurationBase):
    pass


class ConfigurationUpdate(BaseModel):
    context: Optional[str] = None


class ConfigurationResponse(ConfigurationBase):
    id: int
    user: UserResponse
    project: ProjectResponse

    model_config = {"from_attributes": True}
