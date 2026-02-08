from pydantic import BaseModel, field_validator, ConfigDict
import base64
from typing import Any


class ReportCreate(BaseModel):
    data: str

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_bytes(self) -> bytes:
        """Convert base64 string to bytes"""
        try:
            return base64.b64decode(self.data)
        except Exception:
            raise ValueError("Invalid base64 data")


class ReportResponse(BaseModel):
    id: int
    data: bytes

    model_config = ConfigDict(from_attributes=True)
