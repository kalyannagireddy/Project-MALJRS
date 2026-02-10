"""
AI Output Parser - Normalization Layer
Converts raw LLM/CrewAI output into validated Pydantic schema structures.

This module bridges the gap between unstructured AI output and strict API response models,
ensuring that no matter what the LLM returns, the API always returns valid responses.
"""
import logging
import json
from typing import Any, Dict, List, Optional
from models.response_models import PrecedentCase

logger = logging.getLogger("maljrs.parser")


def normalize_classification(value: Any) -> str:
    """
    Normalize classification to lowercase 'civil' or 'criminal'.
    
    Args:
        value: Any input value
        
    Returns:
        Lowercase classification string
    """
    if not value:
        return "civil"
    
    str_value = str(value).lower().strip()
    if "criminal" in str_value:
        return "criminal"
    return "civil"


def normalize_string(value: Any) -> str:
    """
    Convert any value to a string safely.
    
    Args:
        value: Any input value (list, dict, str, etc.)
        
    Returns:
        String representation
    """
    if isinstance(value, str):
        return value.strip()
    elif isinstance(value, list):
        # Join list items with newlines
        return "\n".join(str(item) for item in value)
    elif isinstance(value, dict):
        # Convert dict to formatted string
        return json.dumps(value, indent=2)
    else:
        return str(value)


def normalize_law_dict(value: Any) -> Dict[str, str]:
    """
    Convert law reference to structured dict.
    
    Args:
        value: String like "Act Name - Section X" or existing dict
        
    Returns:
        Dict with 'act', 'section', 'description' keys
    """
    if isinstance(value, dict):
        # Already a dict, ensure required keys
        return {
            "act": str(value.get("act", value.get("actName", "Unknown Act"))),
            "section": str(value.get("section", value.get("sectionNumber", ""))),
            "description": str(value.get("description", ""))
        }
    
    # Parse string format: "Act Name - Section X"
    str_value = str(value)
    parts = str_value.split(" - ", 1)
    
    return {
        "act": parts[0].strip() if len(parts) > 0 else "Unknown Act",
        "section": parts[1].strip() if len(parts) > 1 else "",
        "description": str_value
    }


def normalize_precedent_case(value: Any) -> Dict[str, Any]:
    """
    Convert precedent reference to PrecedentCase structure.
    
    Args:
        value: String, dict, or PrecedentCase object
        
    Returns:
        Dict compatible with PrecedentCase model
    """
    if isinstance(value, dict):
        # Ensure all required fields exist
        return {
            "caseName": str(value.get("caseName", value.get("name", "Unknown Case"))),
            "citation": str(value.get("citation", "Citation not available")),
            "court": str(value.get("court", "Unknown Court")),
            "year": int(value.get("year", 2024)) if isinstance(value.get("year"), (int, str)) else 2024,
            "headnote": str(value.get("headnote", "")),
            "holding": str(value.get("holding", "")),
            "relevance": str(value.get("relevance", "Relevant precedent")),
            "distinction": value.get("distinction")
        }
    
    # Parse string - create placeholder
    case_str = str(value)
    return {
        "caseName": case_str[:100] if len(case_str) > 100 else case_str,
        "citation": "To be determined",
        "court": "To be researched",
        "year": 2024,
        "headnote": case_str,
        "holding": "Analysis pending",
        "relevance": "Requires further research",
        "distinction": None
    }


def normalize_action_plan_item(value: Any) -> Dict[str, str]:
    """
    Convert action plan item to structured dict.
    
    Args:
        value: String or existing dict
        
    Returns:
        Dict with 'action', 'priority', 'timeline' keys
    """
    if isinstance(value, dict):
        return {
            "action": str(value.get("action", value.get("title", str(value)))),
            "priority": str(value.get("priority", "Medium")),
            "timeline": str(value.get("timeline", "To be determined"))
        }
    
    # Create from string
    return {
        "action": str(value),
        "priority": "Medium",
        "timeline": "To be determined"
    }


def parse_full_analysis_response(raw_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and normalize raw AI output into FullAnalysisResponse structure.
    
    This is the main normalization function that ensures all data types match
    the Pydantic model requirements.
    
    Args:
        raw_output: Raw dict from AI service (may have mismatched types)
        
    Returns:
        Normalized dict ready for FullAnalysisResponse validation
    """
    logger.info("=== NORMALIZING AI OUTPUT ===")
    logger.debug(f"Raw output keys: {list(raw_output.keys())}")
    
    # Extract the result dict (handle nested structure)
    result = raw_output.get("result", raw_output)
    
    # Normalize each field according to FullAnalysisReport schema
    normalized = {
        "classification": normalize_classification(result.get("classification", "civil")),
        "executiveSummary": normalize_string(result.get("executiveSummary", "Analysis pending")),
        "keyFacts": normalize_string(result.get("keyFacts", [])),
        "applicableLaws": [
            normalize_law_dict(law) 
            for law in (result.get("applicableLaws", []) if isinstance(result.get("applicableLaws"), list) else [])
        ],
        "precedents": [
            normalize_precedent_case(case)
            for case in (result.get("precedents", []) if isinstance(result.get("precedents"), list) else [])
        ],
        "constitutionalAspects": result.get("constitutionalAspects"),
        "actionPlan": [
            normalize_action_plan_item(item)
            for item in (result.get("actionPlan", []) if isinstance(result.get("actionPlan"), list) else [])
        ],
        "timeline": normalize_string(result.get("timeline", "Timeline not available")),
        "disclaimers": normalize_string(result.get("disclaimers", "This is an AI-generated analysis. Consult a legal professional."))
    }
    
    logger.info("✓ Normalization complete")
    logger.debug(f"Normalized keys: {list(normalized.keys())}")
    
    return normalized


def create_mock_full_analysis(case_data: Any) -> Dict[str, Any]:
    """
    Create a properly structured mock response when AI is unavailable.
    
    Args:
        case_data: CaseData object from frontend
        
    Returns:
        Fully normalized mock response dict
    """
    # Build mock data using actual case data
    mock_result = {
        "classification": "civil",
        "executiveSummary": "AI analysis system is currently unavailable. Please configure the AI crew module to enable intelligent legal analysis.",
        "keyFacts": "\n".join(case_data.claims) if case_data.claims else "No claims provided",
        "applicableLaws": [
            {
                "act": law.actName,
                "section": law.sectionNumber,
                "description": law.description
            }
            for law in (case_data.lawSections or [])
        ] or [{"act": "Not specified", "section": "", "description": "No laws provided"}],
        "precedents": [
            {
                "caseName": "Precedent research unavailable",
                "citation": "N/A",
                "court": "System configuration required",
                "year": 2024,
                "headnote": "AI system not configured",
                "holding": "Please set up CrewAI agents",
                "relevance": "Configuration needed",
                "distinction": None
            }
        ],
        "constitutionalAspects": None,
        "actionPlan": [
            {
                "action": "Configure AI crew module",
                "priority": "High",
                "timeline": "Before system use"
            },
            {
                "action": "Install required dependencies (llm module)",
                "priority": "High",
                "timeline": "Immediate"
            }
        ],
        "timeline": "\n".join(
            f"{event.date}: {event.description}" 
            for event in (case_data.timeline[:5] if case_data.timeline else [])
        ) or "No timeline provided",
        "disclaimers": "This is a placeholder response. The AI analysis system is not currently configured. Please contact your administrator to set up CrewAI integration."
    }
    
    return mock_result
