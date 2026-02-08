from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import Report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/")
async def create_report(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_content = await file.read()
    new_report = Report(data=file_content)
    db.add(new_report)
    db.commit()
    return {"id": new_report.id}
