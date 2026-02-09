# tasks.py
import json
from crewai import Task
from agents import *

# Load KB
with open("data/legal_knowledge_base.json") as f:
    KB = json.load(f)

def create_classifier_task(victim_input: str):
    return Task(
        description=f"""Analyze the legal narrative and classify it as either 'civil' or 'criminal' case.
        Provide detailed reasoning for your classification.
        
        USER NARRATIVE:
        {victim_input}
        
        Provide your analysis in JSON format with:
        - classification: 'civil' or 'criminal'
        - confidence_score: 0-100
        - rationale: Detailed explanation (3-5 sentences) of why this classification applies
        - key_signals: List 3-5 specific indicators from the narrative
        - alternative_considerations: Any reasons why it might also be classified differently""",
        expected_output="Complete JSON object with classification, confidence_score, detailed rationale, key_signals array, and alternative_considerations",
        agent=CLASSIFIER_AGENT
    )

def create_civil_tasks(victim_input: str):
    return [
        Task(
            description=f"""Extract comprehensive structured facts from the civil case narrative.
            Analyze all parties, relationships, timeline of events, claims, and available evidence.
            
            USER NARRATIVE:
            {victim_input}
            
            Provide detailed JSON output including:
            - parties: Complete list with roles, names/descriptions, and relationships
            - dates: Chronological timeline of all events (mark inferred dates clearly)
            - claims: Specific relief sought with legal basis
            - evidence: All mentioned or implied evidence (documents, witnesses, communications)
            - uncertainties: Gaps or ambiguities that need clarification
            - derivation_notes: Detailed explanation of how you interpreted the narrative
            
            Be thorough and include all relevant details for building a strong legal case.""",
            expected_output="Comprehensive JSON with parties (roles, names, relationships), dates (chronological with inferred flag), detailed claims, all evidence types, uncertainties, and thorough derivation notes",
            agent=civil_fact_interpreter
        ),
        Task(
            description="""Map the extracted civil facts to applicable Indian statutes and procedural rules.
            Provide comprehensive legal analysis with specific section citations.
            
            For each applicable law, provide:
            - Full statute name and specific section numbers
            - Detailed explanation of applicability to the case facts
            - Key provisions including limitation periods, jurisdiction, and available remedies
            - Case-specific analysis of how the facts satisfy legal elements
            - Priority ranking based on strength of application
            
            Consider:
            - Civil Procedure Code (CPC)
            - Limitation Act
            - Specific Act (e.g., Hindu Marriage Act, Contract Act, Property laws)
            - Relevant state-specific legislation
            
            Prioritize laws that offer strongest remedies and immediate relief.""",
            expected_output="Detailed prioritized list of statutes with: Full citation, comprehensive applicability explanation (3-5 sentences), key provisions with specific details, case-fact mapping analysis",
            agent=civil_law_mapper,
            context=[]
        ),
        Task(
            description=f"""Find and analyze 3-5 relevant civil case precedents that support the legal analysis.
            Focus on Supreme Court and High Court judgments that directly relate to the facts and laws identified.
            
            REFERENCE CASES TO CONSIDER:
            {', '.join(KB['sample_cases']['civil'])}
            
            For each case, provide:
            - Full case name with complete citation (Court, Year, Journal Reference)
            - Detailed headnote (4-6 sentences summarizing the case)
            - Precise holding/ruling of the court
            - Comprehensive relevance analysis (5-7 sentences) explaining:
              * How the case facts parallel the current situation
              * What legal principles were established
              * How this strengthens the current case
            - Any distinctions or limitations
            - Quotable dicta or key observations from the judgment
            
            Prioritize cases that offer strongest analogies and favorable outcomes.""",
            expected_output="3-5 detailed case analyses with: Full citation, comprehensive headnote, precise holding, detailed relevance analysis (5-7 sentences), distinctions, and key judicial observations",
            agent=civil_precedent_finder,
            context=[]
        )
    ]

def create_criminal_tasks(victim_input: str):
    return [
        Task(
            description=f"""Extract comprehensive structured facts from the criminal case narrative.
            Conduct thorough analysis of all criminal elements, parties, evidence, and safety concerns.
            
            USER NARRATIVE:
            {victim_input}
            
            Provide detailed JSON output including:
            - offenses: Specific suspected IPC sections with brief descriptions
            - accused: Complete details (identity, role, relationship to victim)
            - injuries: Physical and psychological injuries with severity
            - threats: All threats made (explicit and implied)
            - location: Detailed location information and jurisdiction
            - dates: Precise timeline of all criminal acts
            - evidence: Comprehensive list (witnesses, medical records, digital evidence, forensics)
            - safety_alert: Risk level (High/Medium/Low) with justification
            - immediate_actions: Prioritized urgent steps for victim safety
            - modus_operandi: How the offense was committed
            
            Prioritize victim safety and collect all details needed for FIR and investigation.""",
            expected_output="Comprehensive JSON with all criminal elements: offenses (IPC sections), accused details, injuries (physical/psychological), threats, location, timeline, complete evidence list, safety assessment with reasoning, immediate actions, and modus operandi",
            agent=criminal_fact_interpreter
        ),
        Task(
            description="""Map criminal facts to specific IPC sections and outline comprehensive criminal procedure.
            Provide detailed legal framework analysis for prosecution.
            
            For each identified offense, provide:
            - Complete IPC section with full text of relevant provisions
            - Detailed elements analysis (what must be proved)
            - Comprehensive fact-to-element mapping showing how facts satisfy each element
            - Classification: Cognizable/Non-cognizable, Bailable/Non-bailable, Compoundable/Non-compoundable
            - Punishment provisions and sentencing guidelines
            - Related CrPC sections for procedure
            
            PROCEDURAL ANALYSIS:
            - FIR filing process and station jurisdiction
            - Investigation timeline and victim rights
            - Arrest procedures and bail provisions
            - Trial procedure and evidence requirements
            - Victim protection measures and compensation
            - Appeal rights and timelines
            
            Provide step-by-step procedural guidance prioritizing victim safety.""",
            expected_output="Comprehensive legal analysis: Multiple IPC sections with full provisions, detailed elements and fact mapping, complete classification, punishment details, related CrPC sections, and thorough procedural guidance (FIR to appeal) with timelines",
            agent=criminal_law_mapper,
            context=[]
        ),
        Task(
            description=f"""Find and analyze 3-5 relevant criminal case precedents that support prosecution.
            Focus on cases involving similar offenses, evidence interpretation, and sentencing guidelines.
            
            REFERENCE CASES TO CONSIDER:
            {', '.join(KB['sample_cases']['criminal'])}
            
            For each case, provide:
            - Full case name with complete citation (Court, Year, Criminal Appeal No.)
            - Comprehensive case summary (5-7 sentences covering facts, charges, trial, and outcome)
            - Detailed holding on key legal points
            - Relevance analysis (6-8 sentences) explaining:
              * Factual similarities to current case
              * Legal principles established
              * Evidence evaluation standards applied
              * Sentencing considerations
              * How this precedent strengthens prosecution
            - Statutory interpretation notes from the judgment
            - Key observations on victim rights or procedural protections
            
            Prioritize cases favorable to victim/prosecution with strong evidentiary standards.""",
            expected_output="3-5 comprehensive case analyses with: Full citation, detailed summary (5-7 sentences), holdings, extensive relevance analysis (6-8 sentences), statutory interpretation, and victim rights observations",
            agent=criminal_precedent_finder,
            context=[]
        )
    ]

def create_shared_tasks(track_output: str, case_type: str):
    const_principles = KB["constitutional_principles"][case_type]
    procedures = KB["civil_procedures"].get("default", KB["civil_procedures"]["family"]) if case_type == "civil" else KB["criminal_procedures"]["default"]
    
    return [
        Task(
            description=f"""Conduct comprehensive constitutional analysis for fundamental rights violations.
            Review Articles 14 (Equality), 15 (Non-discrimination), 19 (Freedoms), and 21 (Life and Liberty).
            
            CONSTITUTIONAL PRINCIPLES FOR THIS CASE TYPE:
            {const_principles}
            
            For each potentially violated article:
            - Article number and full text of relevant clause
            - Detailed analysis (5-7 sentences) of how the situation violates this right
            - Landmark Supreme Court precedents interpreting this article
            - Available constitutional remedies:
              * Writ petitions (Habeas Corpus, Mandamus, Prohibition, Certiorari, Quo Warranto)
              * Public Interest Litigation (PIL) possibilities
              * Specific relief under Article 32 or 226
            - Procedural requirements for filing constitutional remedy
            - Success likelihood and strategic considerations
            
            If no constitutional violation exists, explain why in detail (3-4 sentences).
            
            Provide practical guidance on when constitutional remedy is preferable to regular legal recourse.""",
            expected_output="Comprehensive constitutional analysis: Each applicable article with full text, detailed violation analysis (5-7 sentences), landmark precedents, available writs with filing procedures, success assessment, and strategic guidance",
            agent=constitutional_validator,
            context=[]
        ),
        Task(
            description=f"""Create a comprehensive, practical action plan with detailed step-by-step guidance.
            Develop 5-12 concrete steps covering immediate actions through final resolution.
            
            PROCEDURAL FRAMEWORK:
            {procedures}
            
            For each step, provide:
            - Step number and clear action title
            - Detailed description (4-6 sentences) of exactly what to do
            - Specific timeline (e.g., "Within 24 hours", "Week 1-2", "Before 30 days")
            - Required documents and forms (with official names/numbers)
            - Where to file/submit (specific court/office/department)
            - Estimated costs (filing fees, lawyer fees, other expenses)
            - Common pitfalls to avoid
            - Success tips and best practices
            
            INCLUDE:
            - Immediate safety measures (if applicable)
            - Documentation and evidence collection
            - Filing procedures with detailed forms list
            - Court appearances and what to expect
            - Follow-up actions and monitoring
            - Alternative dispute resolution options (if applicable)
            - Appeals process and timeline
            
            PROVIDE TEMPLATES for:
            - Complaint/Petition draft (200-300 words)
            - FIR text (if criminal)
            - Demand letter (if civil)
            - Affidavit sample
            
            Make guidance accessible for non-lawyers but legally sound.""",
            expected_output="Comprehensive 5-12 step action plan with: Detailed descriptions (4-6 sentences each), specific timelines, complete documents list, filing locations, cost estimates, templates (200-300 words each), pitfalls, and success tips",
            agent=legal_pathway_advisor,
            context=[]
        ),
        Task(
            description=f"""Synthesize all agent outputs into a comprehensive, professional legal guidance report.
            Create a detailed {case_type.upper()} case report that is both thorough and accessible.
            
            STRUCTURE YOUR REPORT WITH THESE SECTIONS:
            
            1. EXECUTIVE SUMMARY (150-200 words)
               - Overview of situation and key legal standing
               - Primary causes of action
               - Likelihood of success
               - Critical next steps
            
            2. DETAILED FACT SUMMARY (200-300 words)
               - Chronological narrative of events
               - Parties involved with relationships
               - Evidence and documentation available
               - Gaps or uncertainties
            
            3. COMPREHENSIVE LEGAL ANALYSIS (300-400 words)
               - All applicable laws with detailed explanations
               - Why each law applies to the specific facts
               - Elements that must be proved
               - Strengths and weaknesses of legal position
            
            4. PRECEDENT ANALYSIS (250-350 words)
               - Detailed summary of each relevant case
               - How precedents support the current case
               - Key legal principles established
               - Quotable observations from judgments
            
            5. CONSTITUTIONAL DIMENSIONS (If applicable, 150-200 words)
               - Fundamental rights implications
               - Available constitutional remedies
               - Strategic considerations
            
            6. STRATEGIC ACTION PLAN (400-500 words)
               - Complete step-by-step guide
               - Timelines and deadlines
               - Required documents and costs
               - Templates and drafts
            
            7. EVIDENCE & DOCUMENTATION CHECKLIST
               - Complete list of needed evidence
               - How to obtain each item
               - Preservation guidelines
            
            8. ESTIMATED TIMELINE & OUTCOMES (100-150 words)
               - Realistic timeline for resolution
               - Best-case, likely, and worst-case scenarios
               - Factors affecting duration
            
            9. IMPORTANT DISCLAIMERS & RESOURCES
               - Legal disclaimer
               - Helpline numbers and legal aid contacts
               - Additional resources
            
            TONE & STYLE:
            - Use clear, accessible language
            - Explain legal terms when first used
            - Be empathetic but professional
            - Make action items prominent and actionable
            - Use bullet points and formatting for readability
            
            Ensure all sections are comprehensive, well-researched, and provide actionable guidance.""",
            expected_output="Comprehensive 2000-2500 word legal report with 9 detailed sections: Executive Summary (150-200 words), Detailed Facts (200-300 words), Legal Analysis (300-400 words), Precedent Analysis (250-350 words), Constitutional (150-200 words), Action Plan (400-500 words), Evidence Checklist, Timeline (100-150 words), and Disclaimers. Must be well-formatted, accessible, and actionable.",
            agent=report_synthesizer,
            context=[]
        )
    ]