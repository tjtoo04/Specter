from pydantic import BaseModel


class ReportCreate(BaseModel):
    data: bytes


class ReportResponse(BaseModel):
    id: int
    data: bytes

    model_config = {"from_attributes": True}
