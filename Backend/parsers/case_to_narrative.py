"""
Parser to convert structured CaseData to natural language narrative.
This is the critical bridge between frontend structured input and backend AI agents.
"""
from models.case_models import CaseData, TimelineEvent, EvidenceItem, WitnessInfo


def case_to_narrative(case_data: CaseData) -> str:
    """
    Convert structured CaseData from frontend into a natural language narrative
    that can be processed by the existing multi-agent system.
    
    This function intelligently composes a coherent legal narrative from
    structured data, preserving all details while making it readable for AI agents.
    
    Args:
        case_data: Structured case data from frontend
        
    Returns:
        Natural language narrative suitable for AI agent processing
    """
    narrative_parts = []
    
    # Header
    narrative_parts.append("="* 60)
    narrative_parts.append("LEGAL CASE NARRATIVE")
    narrative_parts.append("="* 60)
    narrative_parts.append("")
    
    # Section 1: Basic Case Information
    narrative_parts.append("CASE INFORMATION")
    narrative_parts.append("-" * 40)
    narrative_parts.append(f"Case Title: {case_data.caseTitle}")
    narrative_parts.append(f"Case Type: {case_data.caseType}")
    narrative_parts.append(f"Court/Jurisdiction: {case_data.courtJurisdiction}")
    narrative_parts.append(f"Current Stage: {case_data.stageOfCase}")
    narrative_parts.append(f"Plaintiff/Complainant: {case_data.plaintiffName}")
    narrative_parts.append(f"Defendant/Respondent: {case_data.defendantName}")
    narrative_parts.append("")
    
    # Section 2: Timeline of Events
    if case_data.timeline:
        narrative_parts.append("TIMELINE OF EVENTS")
        narrative_parts.append("-" * 40)
        # Sort timeline by date
        sorted_timeline = sorted(case_data.timeline, key=lambda e: e.date)
        for i, event in enumerate(sorted_timeline, 1):
            proof_marker = " [PROOF AVAILABLE]" if event.proofAvailable else ""
            narrative_parts.append(f"{i}. Date: {event.date}")
            narrative_parts.append(f"   Event: {event.description}")
            if event.peopleInvolved:
                narrative_parts.append(f"   People Involved: {event.peopleInvolved}")
            narrative_parts.append(f"   Evidence Status:{proof_marker}")
            narrative_parts.append("")
    
    # Section 3: Claims and Relief Sought
    if case_data.claims or case_data.reliefRequested:
        narrative_parts.append("CLAIMS AND RELIEF SOUGHT")
        narrative_parts.append("-" * 40)
        if case_data.claims:
            narrative_parts.append("Specific Claims:")
            for i, claim in enumerate(case_data.claims, 1):
                narrative_parts.append(f"{i}. {claim}")
        if case_data.reliefRequested:
            narrative_parts.append(f"\nRelief Requested: {case_data.reliefRequested}")
        narrative_parts.append("")
    
    # Section 4: Evidence Available
    if case_data.evidence:
        narrative_parts.append("EVIDENCE AVAILABLE")
        narrative_parts.append("-" * 40)
        # Group evidence by type
        evidence_by_type = {}
        for evidence in case_data.evidence:
            if evidence.type not in evidence_by_type:
                evidence_by_type[evidence.type] = []
            evidence_by_type[evidence.type].append(evidence)
        
        for evidence_type, items in evidence_by_type.items():
            narrative_parts.append(f"\n{evidence_type} Evidence:")
            for evidence in items:
                narrative_parts.append(f"  - {evidence.description or evidence.fileName}")
                narrative_parts.append(f"    Strength: {evidence.strength}")
                if evidence.linkedTimelineEventId:
                    # Find linked timeline event
                    linked_event = next(
                        (e for e in case_data.timeline if e.id == evidence.linkedTimelineEventId),
                        None
                    )
                    if linked_event:
                        narrative_parts.append(f"    Related to event on: {linked_event.date}")
        narrative_parts.append("")
    
    # Section 5: Legal Issues Identified
    if case_data.legalIssues:
        narrative_parts.append("LEGAL ISSUES IDENTIFIED")
        narrative_parts.append("-" * 40)
        for i, issue in enumerate(case_data.legalIssues, 1):
            narrative_parts.append(f"{i}. {issue}")
        narrative_parts.append("")
    
    # Section 6: Applicable Laws and Sections
    if case_data.lawSections:
        narrative_parts.append("APPLICABLE LAWS AND SECTIONS")
        narrative_parts.append("-" * 40)
        for law in case_data.lawSections:
            narrative_parts.append(f"- {law.actName}, {law.sectionNumber}")
            if law.description:
                narrative_parts.append(f"  Description: {law.description}")
        narrative_parts.append("")
    
    # Section 7: Case Strengths and Weaknesses
    if case_data.strengths or case_data.weaknesses:
        narrative_parts.append("CASE ASSESSMENT")
        narrative_parts.append("-" * 40)
        if case_data.strengths:
            narrative_parts.append("Strengths:")
            narrative_parts.append(case_data.strengths)
            narrative_parts.append("")
        if case_data.weaknesses:
            narrative_parts.append("Weaknesses:")
            narrative_parts.append(case_data.weaknesses)
            narrative_parts.append("")
    
    # Section 8: Witnesses
    if case_data.witnesses:
        narrative_parts.append("WITNESSES")
        narrative_parts.append("-" * 40)
        for i, witness in enumerate(case_data.witnesses, 1):
            narrative_parts.append(f"{i}. {witness.name}")
            narrative_parts.append(f"   Knowledge/Testimony: {witness.knowledge}")
            if witness.linkedTimelineEventId:
                linked_event = next(
                    (e for e in case_data.timeline if e.id == witness.linkedTimelineEventId),
                    None
                )
                if linked_event:
                    narrative_parts.append(f"   Can testify about event on: {linked_event.date}")
            narrative_parts.append("")
    
    # Section 9: AI Assistance Requested
    if case_data.aiAssistance:
        narrative_parts.append("AI ASSISTANCE REQUESTED")
        narrative_parts.append("-" * 40)
        narrative_parts.append("The user has requested assistance with:")
        for i, assistance in enumerate(case_data.aiAssistance, 1):
            narrative_parts.append(f"{i}. {assistance}")
        narrative_parts.append("")
    
    # Footer
    narrative_parts.append("="* 60)
    narrative_parts.append("END OF CASE NARRATIVE")
    narrative_parts.append("="* 60)
    
    return "\n".join(narrative_parts)


def create_focused_narrative(
    case_data: CaseData, 
    focus: str,
    include_structured_context: bool = True
) -> tuple[str, dict]:
    """
    Create a focused narrative for specific AI tasks with structured context.
    
    Args:
        case_data: Full case data from frontend
        focus: Task type ("legal_issues", "precedents", "arguments", "weaknesses", etc.)
        include_structured_context: Whether to return structured context dict
        
    Returns:
        tuple: (narrative_string, structured_context_dict)
    """
    # Build base structured context
    context = {
        "case_type": case_data.caseType,
        "court": case_data.courtJurisdiction,
        "stage": case_data.stageOfCase,
        "parties": {
            "plaintiff": case_data.plaintiffName,
            "defendant": case_data.defendantName
        },
        "stats": {
            "timeline_events": len(case_data.timeline),
            "claims": len(case_data.claims),
            "evidence_items": len(case_data.evidence),
            "witnesses": len(case_data.witnesses),
            "identified_laws": len(case_data.lawSections)
        }
    }
    
    # Start with basic case info
    narrative = f"Case: {case_data.caseTitle}\n"
    narrative += f"Type: {case_data.caseType}\n"
    narrative += f"Parties: {case_data.plaintiffName} vs {case_data.defendantName}\n\n"
    
    # Task-specific narrative building
    if focus == "legal_issues":
        narrative += _build_issue_narrative(case_data)
        context["evidence_items"] = [
            {
                "type": e.type,
                "strength": e.strength,
                "description": e.description,
                "linked_event_id": e.linkedTimelineEventId
            } for e in case_data.evidence
        ]
        
    elif focus == "precedents":
        narrative += _build_precedent_narrative(case_data)
        context["legal_issues"] = case_data.legalIssues
        context["law_sections"] = [
            {
                "act": law.actName,
                "section": law.sectionNumber,
                "description": law.description
            } for law in case_data.lawSections
        ]
        
    elif focus == "arguments":
        narrative += case_to_narrative(case_data)
        context["strengths"] = case_data.strengths
        context["evidence_breakdown"] = _get_evidence_breakdown(case_data)
        
    elif focus == "weaknesses":
        narrative += _build_weakness_narrative(case_data)
        context["evidence_gaps"] = _analyze_evidence_gaps(case_data)
        context["timeline_gaps"] = _analyze_timeline_gaps(case_data)
        context["witness_coverage"] = _analyze_witness_coverage(case_data)
    
    elif focus == "court_notes":
        narrative += case_to_narrative(case_data)
        context["formal_requirements"] = {
            "timeline_count": len(case_data.timeline),
            "evidence_count": len(case_data.evidence),
            "witness_count": len(case_data.witnesses)
        }
    
    elif focus == "cross_questions":
        narrative += _build_cross_question_narrative(case_data)
        context["witnesses_detail"] = [
            {
                "name": w.name,
                "knowledge": w.knowledge,
                "linked_event_id": w.linkedTimelineEventId
            } for w in case_data.witnesses
        ]
    
    else:
        # Default: use full narrative
        narrative = case_to_narrative(case_data)
    
    return (narrative, context) if include_structured_context else (narrative, {})


# Helper narrative builders for specific focus areas

def _build_issue_narrative(case_data: CaseData) -> str:
    """Build narrative focused on legal issue identification"""
    parts = []
    parts.append("KEY FACTS FOR ISSUE IDENTIFICATION:")
    parts.append("-" * 40)
    
    # Timeline with emphasis on legal significance
    if case_data.timeline:
        parts.append("\nCHRONOLOGY:")
        for event in sorted(case_data.timeline, key=lambda e: e.date):
            proof = " [VERIFIED]" if event.proofAvailable else " [ALLEGED]"
            parts.append(f"- {event.date}: {event.description}{proof}")
    
    # Claims analysis
    if case_data.claims:
        parts.append(f"\nCLAIMS FILED: {', '.join(case_data.claims)}")
        parts.append(f"RELIEF SOUGHT: {case_data.reliefRequested}")
    
    # Evidence strength overview
    if case_data.evidence:
        strong = sum(1 for e in case_data.evidence if e.strength == "Strong")
        medium = sum(1 for e in case_data.evidence if e.strength == "Medium")
        weak = sum(1 for e in case_data.evidence if e.strength == "Weak")
        parts.append(f"\nEVIDENCE STRENGTH: {strong} Strong, {medium} Medium, {weak} Weak")
    
    return "\n".join(parts) + "\n"


def _build_precedent_narrative(case_data: CaseData) -> str:
    """Build narrative focused on precedent finding"""
    parts = []
    parts.append("PRECEDENT SEARCH CRITERIA:")
    parts.append("-" * 40)
    
    if case_data.legalIssues:
        parts.append("\nLEGAL ISSUES IDENTIFIED:")
        for i, issue in enumerate(case_data.legalIssues, 1):
            parts.append(f"{i}. {issue}")
    
    if case_data.lawSections:
        parts.append("\nAPPLICABLE STATUTES:")
        for law in case_data.lawSections:
            parts.append(f"- {law.actName}, {law.sectionNumber}")
            if law.description:
                parts.append(f"  ({law.description})")
    
    # Add jurisdiction and case type for precedent filtering
    parts.append(f"\nJURISDICTION: {case_data.courtJurisdiction}")
    parts.append(f"CASE TYPE: {case_data.caseType}")
    
    return "\n".join(parts) + "\n"


def _build_weakness_narrative(case_data: CaseData) -> str:
    """Build narrative focused on weakness analysis"""
    parts = []
    parts.append("CASE WEAKNESS ANALYSIS:")
    parts.append("-" * 40)
    
    parts.append(f"\nCLAIMS: {len(case_data.claims)} filed")
    if case_data.claims:
        for claim in case_data.claims:
            parts.append(f"  - {claim}")
    
    parts.append(f"\nEVIDENCE: {len(case_data.evidence)} items")
    parts.append(f"WITNESSES: {len(case_data.witnesses)} available")
    
    if case_data.weaknesses:
        parts.append(f"\nUSER-IDENTIFIED WEAKNESSES:\n{case_data.weaknesses}")
    
    return "\n".join(parts) + "\n"


def _build_cross_question_narrative(case_data: CaseData) -> str:
    """Build narrative focused on cross-examination question preparation"""
    parts = []
    parts.append("CROSS-EXAMINATION CONTEXT:")
    parts.append("-" * 40)
    
    if case_data.witnesses:
        parts.append("\nWITNESSES TO BE EXAMINED:")
        for i, w in enumerate(case_data.witnesses, 1):
            parts.append(f"{i}. {w.name}")
            parts.append(f"   Knowledge: {w.knowledge}")
            # Link to timeline event if available
            if w.linkedTimelineEventId:
                linked = next((e for e in case_data.timeline if e.id == w.linkedTimelineEventId), None)
                if linked:
                    parts.append(f"   Linked to event: {linked.date} - {linked.description}")
    
    # Include claims for question targeting
    if case_data.claims:
        parts.append(f"\nCLAIMS TO SUPPORT/CHALLENGE: {', '.join(case_data.claims)}")
    
    return "\n".join(parts) + "\n"


# Analytical helper functions

def _analyze_evidence_gaps(case_data: CaseData) -> list[dict]:
    """Identify gaps in evidence coverage across timeline"""
    gaps = []
    
    for event in case_data.timeline:
        # Check if event has proof but no linked evidence
        if not event.proofAvailable:
            linked_evidence = [
                e for e in case_data.evidence 
                if e.linkedTimelineEventId == event.id
            ]
            if not linked_evidence:
                gaps.append({
                    "event_date": event.date,
                    "event_description": event.description,
                    "gap_type": "no_evidence",
                    "severity": "high" if "critical" in event.description.lower() else "medium"
                })
    
    return gaps


def _analyze_timeline_gaps(case_data: CaseData) -> list[dict]:
    """Identify suspicious gaps in timeline chronology"""
    if len(case_data.timeline) < 2:
        return []
    
    from datetime import datetime
    gaps = []
    sorted_timeline = sorted(case_data.timeline, key=lambda e: e.date)
    
    for i in range(len(sorted_timeline) - 1):
        try:
            date1 = datetime.fromisoformat(sorted_timeline[i].date.replace('Z', '+00:00'))
            date2 = datetime.fromisoformat(sorted_timeline[i+1].date.replace('Z', '+00:00'))
            gap_days = (date2 - date1).days
            
            # Flag gaps > 90 days as potentially significant
            if gap_days > 90:
                gaps.append({
                    "from_date": sorted_timeline[i].date,
                    "to_date": sorted_timeline[i+1].date,
                    "gap_days": gap_days,
                    "note": f"{gap_days}-day gap may need explanation"
                })
        except:
            pass  # Skip if date parsing fails
    
    return gaps


def _analyze_witness_coverage(case_data: CaseData) -> dict:
    """Analyze which timeline events are covered by witnesses"""
    coverage = {
        "covered_events": [],
        "uncovered_events": [],
        "witness_count": len(case_data.witnesses)
    }
    
    witness_event_ids = {w.linkedTimelineEventId for w in case_data.witnesses if w.linkedTimelineEventId}
    
    for event in case_data.timeline:
        if event.id in witness_event_ids:
            coverage["covered_events"].append({
                "date": event.date,
                "description": event.description
            })
        else:
            coverage["uncovered_events"].append({
                "date": event.date,
                "description": event.description
            })
    
    return coverage


def _get_evidence_breakdown(case_data: CaseData) -> dict:
    """Get detailed breakdown of evidence by type and strength"""
    breakdown = {}
    
    for evidence in case_data.evidence:
        key = f"{evidence.type}_{evidence.strength}"
        if key not in breakdown:
            breakdown[key] = []
        breakdown[key].append(evidence.description or evidence.fileName)
    
    return breakdown
