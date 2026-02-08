from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from ..database import get_db
from ..models.models import Report
from ..schemas.Report import ReportResponse, ReportCreate
from ..auth import auth

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/", response_model=ReportResponse)
async def create_report(
    report_data: ReportCreate,
    current_user=Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new report from binary data (for AI agent)"""
    new_report = Report(data=report_data.get_bytes())
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    return new_report


@router.get("/", response_model=List[ReportResponse])
async def get_all_reports(
    current_user=Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all reports (metadata only, not file content)"""
    result = await db.execute(select(Report))
    reports = result.scalars().all()
    return reports


@router.get("/{report_id}")
async def get_report(
    report_id: int,
    current_user=Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a specific report file"""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalars().first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return Response(
        content=report.data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=report_{report_id}.bin"},
    )


@router.get("/{report_id}/metadata", response_model=ReportResponse)
async def get_report_metadata(
    report_id: int,
    current_user=Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    """Get report metadata without downloading the file"""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalars().first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    report_data: ReportCreate,
    current_user=Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing report with new binary data"""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalars().first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Update the data
    report.data = report_data.get_bytes()

    await db.commit()
    await db.refresh(report)
    return report


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    current_user=Depends(auth.require_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a report"""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalars().first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    await db.delete(report)
    await db.commit()

    return {"message": "Report deleted successfully"}
