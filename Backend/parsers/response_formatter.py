"""
Response formatter to convert AI agent outputs into structured frontend-friendly format.
"""
import re
import json
from typing import Dict, Any, List, Optional


def format_ai_response(
    raw_output: str, 
    request_type: str,
    structured_context: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Format raw AI agent output into structured format for frontend.
    Enhanced with JSON-first parsing and validation.
    
    Args:
        raw_output: Raw text output from AI agents
        request_type: Type of request (e.g., "full_analysis", "legal_issues", "precedents")
        structured_context: Optional structured context for validation
        
    Returns:
        Structured dictionary suitable for API response
    """
    try:
        # Step 1: Try parsing as JSON first (preferred method)
        json_match = re.search(
            r'```json\s*(\{.*?\})\s*```', 
            raw_output, 
            re.DOTALL
        )
        if json_match:
            parsed = json.loads(json_match.group(1))
            validated = validate_response_structure(parsed, request_type)
            return validated
        
        # Step 2: Look for JSON without code blocks
        try:
            json_start = raw_output.find('{')
            json_end = raw_output.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = raw_output[json_start:json_end]
                parsed = json.loads(json_str)
                validated = validate_response_structure(parsed, request_type)
                return validated
        except json.JSONDecodeError:
            pass
        
        # Step 3: Fallback to legacy extraction methods
        return _fallback_format(raw_output, request_type)
    
    except Exception as e:
        # Return raw output wrapped in error structure
        return {
            "error": "formatting_failed",
            "message": str(e),
            "rawOutput": raw_output
        }


def _fallback_format(raw_output: str, request_type: str) -> Dict[str, Any]:
    """Fallback to legacy regex-based extraction if JSON parsing fails"""
    if request_type == "full_analysis":
        return format_full_analysis(raw_output)
    elif request_type == "legal_issues":
        return format_legal_issues(raw_output)
    elif request_type == "precedents":
        return format_precedents(raw_output)
    elif request_type == "arguments":
        return format_arguments(raw_output)
    elif request_type == "weaknesses":
        return format_weaknesses(raw_output)
    elif request_type == "court_notes":
        return format_court_notes(raw_output)
    elif request_type == "cross_questions":
        return format_cross_questions(raw_output)
    else:
        return {"rawOutput": raw_output}


def validate_response_structure(data: dict, request_type: str) -> dict:
    """
    Validate that parsed response has required fields and correct types.
    
    Args:
        data: Parsed JSON data
        request_type: Expected response type
    
    Returns:
        Validated data dict
    
    Raises:
        ValueError: If validation fails
    """
    validators = {
        "legal_issues": ["identified_issues", "confidence_score"],
        "precedents": ["cases"],
        "arguments": ["arguments"],
        "weaknesses": ["weaknesses"],
        "court_notes": ["notes"],
        "cross_questions": ["questions"]
    }
    
    required_fields = validators.get(request_type, [])
    missing = [f for f in required_fields if f not in data]
    
    if missing:
        raise ValueError(f"Response missing required fields: {missing}")
    
    # Type-specific validation
    if request_type == "legal_issues":
        if "identified_issues" in data and not isinstance(data["identified_issues"], list):
            raise ValueError("identified_issues must be an array")
        if "confidence_score" in data:
            score = data["confidence_score"]
            if not (isinstance(score, (int, float)) and 0.0 <= score <= 1.0):
                raise ValueError("confidence_score must be between 0.0 and 1.0")
    
    elif request_type == "precedents":
        if not isinstance(data["cases"], list):
            raise ValueError("cases must be an array")
    
    return data


def format_full_analysis(raw_output: str) -> Dict[str, Any]:
    """Format complete legal analysis report"""
    return {
        "classification": extract_classification(raw_output),
        "executiveSummary": extract_section(raw_output, "EXECUTIVE SUMMARY"),
        "keyFacts": extract_section(raw_output, "KEY FACTS"),
        "applicableLaws": extract_laws(raw_output),
        "precedents": extract_precedent_cases(raw_output),
        "constitutionalAspects": extract_section(raw_output, "CONSTITUTIONAL"),
        "actionPlan": extract_action_plan(raw_output),
        "timeline": extract_section(raw_output, "TIMELINES"),
        "disclaimers": extract_section(raw_output, "DISCLAIMER"),
        "rawOutput": raw_output
    }


def format_legal_issues(raw_output: str) -> Dict[str, Any]:
    """Extract legal issues from output"""
    issues = []
    # Look for numbered or bulleted lists
    issue_pattern = r'(?:^|\n)(?:\d+\.|\-|\•)\s*(.+?)(?=\n|$)'
    matches = re.findall(issue_pattern, raw_output, re.MULTILINE)
    issues = [m.strip() for m in matches if m.strip()]
    
    return {
        "issues": issues if issues else [raw_output.strip()],
        "confidence": 0.8  # Default confidence
    }


def format_precedents(raw_output: str) -> Dict[str, Any]:
    """Extract precedent cases from output"""
    cases = extract_precedent_cases(raw_output)
    return {"cases": cases}


def format_arguments(raw_output: str) -> Dict[str, Any]:
    """Extract argument points from output"""
    arguments = []
    # Try to extract structured arguments
    # This is a simplified parser - can be enhanced
    sections = raw_output.split('\n\n')
    for section in sections:
        if section.strip():
            arguments.append({
                "title": section.split('\n')[0] if '\n' in section else section[:50],
                "description": section,
                "supportingLaw": "",  # Would need more sophisticated parsing
                "supportingPrecedent": None
            })
    
    return {"arguments": arguments}


def format_weaknesses(raw_output: str) -> Dict[str, Any]:
    """Extract weakness points from output"""
    weaknesses = []
    # Simple extraction - can be enhanced
    lines = raw_output.split('\n')
    for line in lines:
        if line.strip() and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
            weaknesses.append({
                "issue": line.strip().lstrip('0123456789.-•) '),
                "severity": "Medium",  # Default
                "mitigation": "To be determined"
            })
    
    return {"weaknesses": weaknesses}


def format_court_notes(raw_output: str) -> Dict[str, Any]:
    """Extract court notes from output"""
    notes = []
    # Extract sections
    sections = raw_output.split('\n\n')
    for section in sections:
        if section.strip():
            lines = section.split('\n')
            notes.append({
                "section": lines[0] if lines else "Note",
                "content": '\n'.join(lines[1:]) if len(lines) > 1 else section
            })
    
    return {
        "notes": notes,
        "fullDraft": raw_output
    }


def format_cross_questions(raw_output: str) -> Dict[str, Any]:
    """Extract cross-examination questions from output"""
    questions = []
    # Simple extraction
    q_pattern = r'Q\d*[.:]?\s*(.+?)(?=\n|$)'
    matches = re.findall(q_pattern, raw_output, re.MULTILINE | re.IGNORECASE)
    
    for i, q in enumerate(matches):
        questions.append({
            "witnessType": "General",
            "question": q.strip(),
            "purpose": "To establish/challenge facts",
            "expectedAnswer": "Variable"
        })
    
    return {"questions": questions}


# Helper functions

def extract_classification(text: str) -> str:
    """Extract case classification (civil/criminal)"""
    text_lower = text.lower()
    if "criminal" in text_lower:
        return "criminal"
    elif "civil" in text_lower:
        return "civil"
    return "civil"  # Default


def extract_section(text: str, section_name: str) -> str:
    """Extract a specific section from the report"""
    # Look for section header
    pattern = rf'\*?\*?{section_name}\*?\*?[:\s]*(.*?)(?=\n\*?\*?[A-Z\s]+\*?\*?:|$)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def extract_laws(text: str) -> List[Dict[str, str]]:
    """Extract applicable laws from text"""
    laws = []
    # Look for patterns like "Section XX of Act Name"
    pattern = r'(?:Section|Article)\s+(\d+[A-Z]?)\s+of\s+([^,\n]+)'
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    for section, act in matches:
        laws.append({
            "statute": act.strip(),
            "section": f"Section {section}",
            "applicability": ""  # Would need more context to extract
        })
    
    return laws


def extract_precedent_cases(text: str) -> List[Dict[str, str]]:
    """Extract precedent cases from text"""
    cases = []
    # Look for case citations (simplified pattern)
    pattern = r'([A-Z][^v\n]+)\s+v\.?\s+([A-Z][^\n,]+)(?:,?\s*([^\n]+))?'
    matches = re.findall(pattern, text)
    
    for match in matches[:5]:  # Limit to top 5
        cases.append({
            "caseName": f"{match[0].strip()} v. {match[1].strip()}",
            "citation": match[2].strip() if len(match) > 2 else "",
            "court": "Supreme Court",  # Default
            "year": 2020,  # Default
            "headnote": "",
            "holding": "",
            "relevance": ""
        })
    
    return cases


def extract_action_plan(text: str) -> List[Dict[str, str]]:
    """Extract action plan steps from text"""
    steps = []
    # Look for numbered steps
    pattern = r'(?:Step\s+)?(\d+)[.:\)]\s*(.+?)(?=\n(?:Step\s+)?\d+[.:\)]|\n\n|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for step_num, step_content in matches:
        steps.append({
            "step": int(step_num),
            "title": step_content.split('\n')[0].strip(),
            "details": step_content.strip(),
            "timeline": "TBD",
            "documents": []
        })
    
    return steps
