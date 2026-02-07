from pydantic import BaseModel


class UserCreate(BaseModel):
    id: str
    name: str
    email: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True
