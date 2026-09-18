"""
Screenings, History, Comparison, Report & Referral Endpoints.

GET  /api/screenings
GET  /api/screenings/{screening_id}
POST /api/screenings/compare
GET  /api/screenings/{screening_id}/report
GET  /api/providers
POST /api/referrals
"""

import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import HTMLResponse

from app.services.db import get_all_screenings, get_screening_by_id
from app.services.comparison import compare_screenings
from app.services.report import generate_html_report
from app.services.referral import list_dental_providers, submit_referral_request

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Screenings & Tracking"])


class CompareRequest(BaseModel):
    previous_screening_id: str = Field(..., description="ID of baseline or previous screening")
    current_screening_id: str = Field(..., description="ID of recent or current screening")


class ReferralRequest(BaseModel):
    screening_id: str = Field(..., description="Associated screening report ID")
    provider_id: str = Field(..., description="Target dental clinic ID")
    patient_name: str = Field(..., description="Patient full name")
    patient_email: str = Field(..., description="Patient email address")
    patient_phone: Optional[str] = Field(None, description="Patient phone number")
    preferred_time: Optional[str] = Field(None, description="Preferred appointment window")
    notes: Optional[str] = Field(None, description="Additional context or symptoms")


@router.get(
    "/api/screenings",
    summary="List all historical screenings",
    description="Returns chronological summary list of past preliminary oral screenings."
)
async def list_screenings():
    return get_all_screenings()


@router.get(
    "/api/screenings/{screening_id}",
    summary="Get full screening details by ID",
    description="Returns complete findings, score breakdown, and linked questionnaire answers."
)
async def get_screening(screening_id: str):
    record = get_screening_by_id(screening_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening '{screening_id}' was not found."
        )
    return record


@router.post(
    "/api/screenings/compare",
    summary="Compare two historical screenings",
    description="Computes category-level visible changes and score change using non-diagnostic language."
)
async def compare_two_screenings(payload: CompareRequest):
    prev_record = get_screening_by_id(payload.previous_screening_id)
    if not prev_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Previous screening '{payload.previous_screening_id}' not found."
        )

    curr_record = get_screening_by_id(payload.current_screening_id)
    if not curr_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Current screening '{payload.current_screening_id}' not found."
        )

    comparison = compare_screenings(prev_record, curr_record)
    return comparison


@router.get(
    "/api/screenings/{screening_id}/report",
    summary="Generate print-friendly HTML dentist report",
    response_class=HTMLResponse,
    description="Renders a high-resolution, print-ready HTML summary report suitable for sharing with a dentist."
)
async def view_dentist_report_html(screening_id: str):
    record = get_screening_by_id(screening_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening '{screening_id}' not found."
        )
    html_content = generate_html_report(record)
    return HTMLResponse(content=html_content, status_code=200)


@router.get(
    "/api/providers",
    summary="List dental care providers for professional evaluation",
    description="Returns verified dental clinics and practices available for appointment referrals."
)
async def get_providers(query: Optional[str] = Query(None, description="Search term")):
    return list_dental_providers(query)


@router.post(
    "/api/referrals",
    summary="Submit patient appointment referral request",
    description="Connects the patient's preliminary screening findings with a dental clinic."
)
async def submit_referral(payload: ReferralRequest):
    return submit_referral_request(
        screening_id=payload.screening_id,
        provider_id=payload.provider_id,
        patient_name=payload.patient_name,
        patient_email=payload.patient_email,
        patient_phone=payload.patient_phone,
        preferred_time=payload.preferred_time,
        notes=payload.notes,
    )
