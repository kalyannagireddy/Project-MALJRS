"""
Case management API routes.
Provides CRUD endpoints for legal cases.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from models.case_models import CaseData, StoredCase
from models.request_models import CreateCaseRequest, UpdateCaseRequest
from models.response_models import CaseResponse, BaseResponse
from services.case_service import CaseService

router = APIRouter(prefix="/api/cases", tags=["cases"])
case_service = CaseService()


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(request: CreateCaseRequest):
    """
    Create a new legal case.
    
    **Frontend Usage**: Called when user starts filling out case information.
    """
    try:
        case_id = case_service.create_case(request.data)
        return CaseResponse(
            success=True,
            message="Case created successfully",
            caseId=case_id,
            status="draft"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create case: {str(e)}"
        )


@router.get("/{case_id}", response_model=StoredCase)
async def get_case(case_id: str):
    """
    Retrieve a case by ID.
    
    **Frontend Usage**: Load saved case data for editing or review.
    """
    case = case_service.get_case(case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found"
        )
    return case


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(case_id: str, request: UpdateCaseRequest):
    """
    Update an existing case.
    
    **Frontend Usage**: Auto-save or manual save of case data.
    """
    if not case_service.case_exists(case_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found"
        )
    
    success = case_service.update_case(case_id, request.data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update case"
        )
    
    # Get updated case to return current status
    updated_case = case_service.get_case(case_id)
    
    return CaseResponse(
        success=True,
        message="Case updated successfully",
        caseId=case_id,
        status=updated_case.status if updated_case else "draft"
    )


@router.delete("/{case_id}", response_model=BaseResponse)
async def delete_case(case_id: str):
    """
    Delete a case.
    
    **Frontend Usage**: Allow users to delete draft cases.
    """
    success = case_service.delete_case(case_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found"
        )
    
    return BaseResponse(
        success=True,
        message=f"Case {case_id} deleted successfully"
    )


@router.get("", response_model=List[str])
async def list_cases():
    """
    List all case IDs.
    
    **Frontend Usage**: Show user's saved cases.
    """
    return case_service.list_cases()
