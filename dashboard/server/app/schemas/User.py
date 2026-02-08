from pydantic import BaseModel


class UserCreate(BaseModel):
    id: str
    username: str
    email: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str

    model_config = {"from_attributes": True}
