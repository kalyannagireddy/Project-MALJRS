"""
AI processing service.
Orchestrates AI analysis based on frontend requests.
"""
import sys
import os
from typing import Dict, Any, List, Optional

# Add parent directory to path to import existing modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.case_models import CaseData
from parsers.case_to_narrative import case_to_narrative, create_focused_narrative
from parsers.response_formatter import format_ai_response
from services.cache_service import get_cache_service
import hashlib
import json
import logging

logger = logging.getLogger("maljrs.ai_service")


class AIService:
    """Service for AI-powered legal analysis with caching and optimized workflows"""
    
    def __init__(self):
        """Initialize AI service with cache"""
        self.cache = get_cache_service()
        self._classifier_cache = {}  # In-memory cache for classifications
        logger.info("AIService initialized with caching enabled")
    
    def _generate_cache_key(self, case_data: CaseData, task_type: str) -> str:
        """Generate cache key from case data and task type"""
        # Use case data fields that affect analysis
        cache_dict = {
            "task": task_type,
            "case_type": case_data.caseType,
            "title": case_data.caseTitle,
            "timeline_count": len(case_data.timeline),
            "evidence_count": len(case_data.evidence),
            "claims": sorted(case_data.claims),
            "legal_issues": sorted(case_data.legalIssues) if case_data.legalIssues else []
        }
        return self.cache.generate_cache_key(cache_dict, prefix=task_type)
    
    def _get_or_run_classification(self, case_data: CaseData) -> str:
        """
        Get cached classification or run classifier agent.
        Cached separately as classification is reused across tasks.
        """
        # Simple hash based on case type and title
        case_hash = hashlib.sha256(
            f"{case_data.caseType}{case_data.caseTitle}".encode()
        ).hexdigest()[:16]
        
        if case_hash in self._classifier_cache:
            logger.debug(f"Using cached classification for {case_hash}")
            return self._classifier_cache[case_hash]
        
        # Run classification
        logger.info(f"Running classifier for case: {case_data.caseTitle}")
        try:
            from main import run_legal_crew
            narrative, _ = create_focused_narrative(case_data, "classification")
            
            # For now, run full crew (will optimize with specialized crews later)
            raw_output = run_legal_crew(narrative)
            
            # Extract classification from output
            classification = self._extract_classification(str(raw_output))
            self._classifier_cache[case_hash] = classification
            
            return classification
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            # Fallback to case_data.caseType
            return case_data.caseType.lower() if case_data.caseType else "civil"
    
    def _extract_classification(self, raw_output: str) -> str:
        """Extract classification from raw AI output"""
        output_lower = raw_output.lower()
        if "criminal" in output_lower:
            return "criminal"
        elif "civil" in output_lower:
            return "civil"
        return "civil"  # Default
    
    def process_full_case(
        self, 
        case_data: CaseData,
        selected_options: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process complete case with full AI analysis.
        Enhanced with caching and structured context preservation.
        
        Args:
            case_data: Case data from frontend
            selected_options: Specific AI assistance options selected
            
        Returns:
            Dictionary with success status and analysis result
        """
        logger.info(f"=== PROCESSING FULL CASE: {case_data.caseTitle} ===")
        logger.info(f"Selected options: {selected_options}")
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(case_data, "full_analysis")
            logger.debug(f"Cache key generated: {cache_key[:16]}...")
            
            # Check cache
            cached = self.cache.get(cache_key)
            if cached:
                logger.info("✓ Returning cached full analysis")
                return {
                    "success": True,
                    "result": cached,
                    "cached": True
                }
            
            logger.info("Cache miss - running full AI analysis")
            
            # Convert to narrative
            narrative, structured_context = create_focused_narrative(
                case_data, 
                focus="full_analysis"
            )
            logger.debug(f"Created narrative ({len(narrative)} chars)")
            
            # Import and run multi-agent system
            try:
                from main import run_legal_crew
                logger.info("Running AI crew analysis...")
                raw_output = run_legal_crew(narrative)
                logger.info(f"AI analysis complete ({len(str(raw_output))} chars)")
                
            except ImportError as e:
                logger.error(f"Failed to import main.run_legal_crew: {e}")
                # Use normalization layer to create properly structured mock response
                from parsers.ai_output_parser import create_mock_full_analysis
                
                normalized_mock = create_mock_full_analysis(case_data)
                logger.info("✓ Generated normalized mock response")
                
                return {
                    "success": True,
                    "result": normalized_mock,
                    "mock": True
                }
            
            # Format response
            formatted = format_ai_response(str(raw_output), "full_analysis")
            logger.debug("Response formatted successfully")
            
            # NORMALIZE OUTPUT - Convert to strict Pydantic schema
            from parsers.ai_output_parser import parse_full_analysis_response
            
            normalized = parse_full_analysis_response({"result": formatted})
            logger.info("✓ AI output normalized for Pydantic validation")
            
            # Cache the normalized result
            self.cache.set(cache_key, normalized, ttl=3600)
            logger.info("✓ Result cached for 1 hour")
            
            return {
                "success": True,
                "result": normalized,
                "narrative": narrative
            }
            
        except Exception as e:
            logger.error(f"FULL CASE PROCESSING ERROR: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def identify_legal_issues(self, case_data: CaseData) -> Dict[str, Any]:
        """
        Identify legal issues using optimized workflow.
        Uses focused narrative and caches results.
        
        Args:
            case_data: Case data from frontend
            
        Returns:
            List of identified legal issues with confidence scores
        """
        # Check cache
        cache_key = self._generate_cache_key(case_data, "legal_issues")
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            logger.info("Returning cached legal issues")
            return {"success": True, "result": cached_result, "from_cache": True}
        
        try:
            # Create focused narrative with structured context
            narrative, context = create_focused_narrative(
                case_data, 
                "legal_issues",
                include_structured_context=True
            )
            
            logger.info(f"Identifying issues for: {case_data.caseTitle}")
            
            # Run AI crew (will optimize to use only necessary agents later)
            from main import run_legal_crew
            raw_output = run_legal_crew(narrative)
            
            # Format with context
            formatted = format_ai_response(
                str(raw_output), 
                "legal_issues",
                structured_context=context
            )
            
            # Cache result (30 minutes)
            self.cache.set(cache_key, formatted, ttl=1800)
            
            return {
                "success": True,
                "result": formatted,
                "from_cache": False
            }
        except Exception as e:
            logger.exception("Legal issue identification failed")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def find_precedents(self, case_data: CaseData) -> Dict[str, Any]:
        """
        Find relevant legal precedents.
        Uses focused narrative emphasizing laws and jurisdiction.
        
        Args:
            case_data: Case data from frontend
            
        Returns:
            List of relevant precedent cases
        """
        cache_key = self._generate_cache_key(case_data, "precedents")
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            logger.info("Returning cached precedents")
            return {"success": True, "result": cached_result, "from_cache": True}
        
        try:
            narrative, context = create_focused_narrative(
                case_data,
                "precedents",
                include_structured_context=True
            )
            
            logger.info(f"Finding precedents for: {case_data.caseTitle}")
            
            from main import run_legal_crew
            raw_output = run_legal_crew(narrative)
            
            formatted = format_ai_response(
                str(raw_output),
                "precedents",
                structured_context=context
            )
            
            # Cache result (1 hour - precedents don't change often)
            self.cache.set(cache_key, formatted, ttl=3600)
            
            return {
                "success": True,
                "result": formatted,
                "from_cache": False
            }
        except Exception as e:
            logger.exception("Precedent finding failed")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def prepare_arguments(self, case_data: CaseData) -> Dict[str, Any]:
        """
        Prepare legal arguments for the case.
        
        Args:
            case_data: Case data from frontend
            
        Returns:
            Structured arguments with supporting evidence
        """
        cache_key = self._generate_cache_key(case_data, "arguments")
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            return {"success": True, "result": cached_result, "from_cache": True}
        
        try:
            narrative, context = create_focused_narrative(
                case_data,
                "arguments",
                include_structured_context=True
            )
            
            logger.info(f"Preparing arguments for: {case_data.caseTitle}")
            
            from main import run_legal_crew
            raw_output = run_legal_crew(narrative)
            
            formatted = format_ai_response(
                str(raw_output),
                "arguments",
                structured_context=context
            )
            
            self.cache.set(cache_key, formatted, ttl=1800)
            
            return {
                "success": True,
                "result": formatted,
                "from_cache": False
            }
        except Exception as e:
            logger.exception("Argument preparation failed")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def find_weaknesses(self, case_data: CaseData) -> Dict[str, Any]:
        """
        Identify weaknesses in the case.
        Uses analytical helpers for gap detection.
        
        Args:
            case_data: Case data from frontend
            
        Returns:
            List of weaknesses with severity and mitigation strategies
        """
        cache_key = self._generate_cache_key(case_data, "weaknesses")
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            return {"success": True, "result": cached_result, "from_cache": True}
        
        try:
            narrative, context = create_focused_narrative(
                case_data,
                "weaknesses",
                include_structured_context=True
            )
            
            logger.info(f"Analyzing weaknesses for: {case_data.caseTitle}")
            logger.debug(f"Evidence gaps: {len(context.get('evidence_gaps', []))}")
            logger.debug(f"Timeline gaps: {len(context.get('timeline_gaps', []))}")
            
            from main import run_legal_crew
            raw_output = run_legal_crew(narrative)
            
            formatted = format_ai_response(
                str(raw_output),
                "weaknesses",
                structured_context=context
            )
            
            self.cache.set(cache_key, formatted, ttl=1800)
            
            return {
                "success": True,
                "result": formatted,
                "from_cache": False
            }
        except Exception as e:
            logger.exception("Weakness analysis failed")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def draft_court_notes(self, case_data: CaseData) -> Dict[str, Any]:
        """
        Draft formal court notes/submissions.
        
        Args:
            case_data: Case data from frontend
            
        Returns:
            Formatted court notes with proper legal structure
        """
        cache_key = self._generate_cache_key(case_data, "court_notes")
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            return {"success": True, "result": cached_result, "from_cache": True}
        
        try:
            narrative, context = create_focused_narrative(
                case_data,
                "court_notes",
                include_structured_context=True
            )
            
            logger.info(f"Drafting court notes for: {case_data.caseTitle}")
            
            from main import run_legal_crew
            raw_output = run_legal_crew(narrative)
            
            formatted = format_ai_response(
                str(raw_output),
                "court_notes",
                structured_context=context
            )
            
            self.cache.set(cache_key, formatted, ttl=3600)
            
            return {
                "success": True,
                "result": formatted,
                "from_cache": False
            }
        except Exception as e:
            logger.exception("Court note drafting failed")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def prepare_cross_questions(self, case_data: CaseData) -> Dict[str, Any]:
        """
        Prepare cross-examination questions.
        
        Args:
            case_data: Case data from frontend
            
        Returns:
            List of cross-examination questions per witness
        """
        cache_key = self._generate_cache_key(case_data, "cross_questions")
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            return {"success": True, "result": cached_result, "from_cache": True}
        
        try:
            narrative, context = create_focused_narrative(
                case_data,
                "cross_questions",
                include_structured_context=True
            )
            
            logger.info(f"Preparing cross-questions for: {case_data.caseTitle}")
            logger.debug(f"Witnesses to examine: {len(case_data.witnesses)}")
            
            from main import run_legal_crew
            raw_output = run_legal_crew(narrative)
            
            formatted = format_ai_response(
                str(raw_output),
                "cross_questions",
                structured_context=context
            )
            
            self.cache.set(cache_key, formatted, ttl=1800)
            
            return {
                "success": True,
                "result": formatted,
                "from_cache": False
            }
        except Exception as e:
            logger.exception("Cross-question preparation failed")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        return self.cache.get_stats()
    
    def clear_cache(self, case_id: Optional[str] = None):
        """Clear cache for specific case or all caches"""
        if case_id:
            self.cache.invalidate_prefix(case_id)
            logger.info(f"Cleared cache for case: {case_id}")
        else:
            self.cache.clear()
            self._classifier_cache.clear()
            logger.info("Cleared all caches")


# Global service instance
_ai_service_instance = None

def get_ai_service() -> AIService:
    """Get or create global AI service instance"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance
