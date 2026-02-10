"""
AI processing API routes.
Provides endpoints for AI-powered legal analysis.
"""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import Dict, Any
import traceback

from models.request_models import AIProcessRequest
from models.response_models import (
    AIProcessingResponse,
    LegalIssuesResponse,
    PrecedentsResponse,
    ArgumentsResponse,
    WeaknessesResponse,
    CourtNotesResponse,
    CrossQuestionsResponse,
    FullAnalysisResponse
)
from services.ai_service import AIService
from services.case_service import CaseService

router = APIRouter(prefix="/api/ai", tags=["ai"])
ai_service = AIService()
case_service = CaseService()


@router.post("/process", response_model=FullAnalysisResponse)
async def process_case(request: AIProcessRequest):
    """
    Process complete case with full AI analysis.
    
    **Frontend Usage**: Called when user submits case on Review page.
    This is the primary endpoint matching frontend's "Submit Case to AI System" button.
    """
    try:
        # Process the case
        result = ai_service.process_full_case(
            request.caseData,
            request.options
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "AI processing failed")
            )
        
        # Create case if it doesn't exist
        case_id = case_service.create_case(request.caseData)
        case_service.update_status(case_id, "completed")
        
        return FullAnalysisResponse(
            success=True,
            message="Case analysis completed",
            caseId=case_id,
            report=result["result"],
            rawOutput=result.get("narrative", "")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"AI PROCESSING ERROR: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during AI processing: {str(e)}"
        )


@router.post("/identify-issues", response_model=LegalIssuesResponse)
async def identify_issues(request: AIProcessRequest):
    """
    Identify legal issues in the case.
    
    **Frontend Usage**: AI Assistance option "Identify legal issues"
    """
    try:
        result = ai_service.identify_legal_issues(request.caseData)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to identify issues")
            )
        
        formatted_result = result["result"]
        return LegalIssuesResponse(
            success=True,
            message="Legal issues identified",
            issues=formatted_result.get("issues", []),
            confidence=formatted_result.get("confidence", 0.8)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error identifying issues: {str(e)}"
        )


@router.post("/find-precedents", response_model=PrecedentsResponse)
async def find_precedents(request: AIProcessRequest):
    """
    Find relevant legal precedents.
    
    **Frontend Usage**: AI Assistance option "Find relevant precedents"
    """
    try:
        result = ai_service.find_precedents(request.caseData)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to find precedents")
            )
        
        formatted_result = result["result"]
        return PrecedentsResponse(
            success=True,
            message="Precedents found",
            cases=formatted_result.get("cases", [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding precedents: {str(e)}"
        )


@router.post("/prepare-arguments", response_model=ArgumentsResponse)
async def prepare_arguments(request: AIProcessRequest):
    """
    Prepare legal arguments.
    
    **Frontend Usage**: AI Assistance option "Prepare arguments"
    """
    try:
        result = ai_service.prepare_arguments(request.caseData)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to prepare arguments")
            )
        
        formatted_result = result["result"]
        return ArgumentsResponse(
            success=True,
            message="Arguments prepared",
            arguments=formatted_result.get("arguments", [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error preparing arguments: {str(e)}"
        )


@router.post("/find-weaknesses", response_model=WeaknessesResponse)
async def find_weaknesses(request: AIProcessRequest):
    """
    Find weaknesses in the case.
    
    **Frontend Usage**: AI Assistance option "Find weaknesses"
    """
    try:
        result = ai_service.find_weaknesses(request.caseData)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to find weaknesses")
            )
        
        formatted_result = result["result"]
        return WeaknessesResponse(
            success=True,
            message="Weaknesses identified",
            weaknesses=formatted_result.get("weaknesses", [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding weaknesses: {str(e)}"
        )


@router.post("/draft-notes", response_model=CourtNotesResponse)
async def draft_notes(request: AIProcessRequest):
    """
    Draft court notes.
    
    **Frontend Usage**: AI Assistance option "Draft court notes"
    """
    try:
        result = ai_service.draft_court_notes(request.caseData)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to draft notes")
            )
        
        formatted_result = result["result"]
        return CourtNotesResponse(
            success=True,
            message="Court notes drafted",
            notes=formatted_result.get("notes", []),
            fullDraft=formatted_result.get("fullDraft", "")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error drafting notes: {str(e)}"
        )


@router.post("/prepare-questions", response_model=CrossQuestionsResponse)
async def prepare_questions(request: AIProcessRequest):
    """
    Prepare cross-examination questions.
    
    **Frontend Usage**: AI Assistance option "Prepare cross-questions"
    """
    try:
        result = ai_service.prepare_cross_questions(request.caseData)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to prepare questions")
            )
        
        formatted_result = result["result"]
        return CrossQuestionsResponse(
            success=True,
            message="Cross-examination questions prepared",
            questions=formatted_result.get("questions", [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error preparing questions: {str(e)}"
        )
