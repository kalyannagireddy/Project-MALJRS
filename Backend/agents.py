# agents.py
from crewai import Agent
import requests
import logging
import time
import asyncio
import aiohttp
import os
from crewai.llms.base_llm import BaseLLM
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# LLMs

logger = logging.getLogger("maljrs.ollama")


class OllamaLLM(BaseLLM):
    """Optimized Ollama LLM client with connection pooling and retry logic."""
    
    def __init__(self, model=None, base_url=None, temperature=None, api_key=None, **kwargs):
        # Get configuration from environment variables with fallbacks
        self.model = model or os.getenv("OLLAMA_MODEL", "gpt-oss:120b")
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "https://ollama.com")).rstrip("/")
        self.temperature = float(temperature) if temperature is not None else float(os.getenv("TEMPERATURE", "0.1"))
        
        # Call parent constructor first
        super().__init__(model=self.model, temperature=self.temperature, base_url=self.base_url, provider="ollama", **kwargs)
        
        # Get API key for Ollama Cloud - AFTER super().__init__() to prevent overwriting
        _api_key = api_key if api_key is not None else os.getenv("OLLAMA_API_KEY")
        self.api_key = _api_key
        
        # Configure session with connection pooling and retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=1,  # Reduced retries for speed
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=15, pool_maxsize=30)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.headers = {"Content-Type": "application/json"}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
            logger.info(f"OllamaLLM initialized with API key - Model: {self.model}, Base URL: {self.base_url}, Temp: {self.temperature}")
        else:
            logger.info(f"OllamaLLM initialized - Model: {self.model}, Base URL: {self.base_url}, Temp: {self.temperature}")
        
        self.call_count = 0
        self.total_tokens = 0
        self.total_time = 0
    
    def supports_stop_words(self) -> bool:
        """Method that returns whether stop words are supported."""
        return False

    def call(
        self,
        messages,
        tools: list[dict] | None = None,
        callbacks: list | None = None,
        available_functions: dict | None = None,
        from_task=None,
        from_agent=None,
        response_model=None,
        **kwargs,
    ) -> str:
        """CrewAI BaseLLM-compatible call method returning response text."""
        # Convert messages to a single prompt string
        if isinstance(messages, list):
            prompt = "\n".join([m.get("content", "") if isinstance(m, dict) else str(m) for m in messages])
        else:
            prompt = str(messages)
        logger.debug(f"LLM call received - Prompt length: {len(prompt)} chars")
        return self.generate(prompt, **kwargs)

    def generate(self, prompt: str, timeout: int = 120, max_retries: int = 1, **kwargs):
        """Use Ollama's REST generate endpoint with optimized connection and retry logic."""
        logger.info(f"Generating response from Ollama - Model: {self.model}")
        start_time = time.time()
        prompt_length = len(prompt)
        
        # Allow longer prompts for detailed analysis
        if prompt_length > 6000:
            logger.warning(f"Prompt too long ({prompt_length} chars), truncating to 6000")
            prompt = prompt[:6000] + "\n[Truncated - provide key details]"
            prompt_length = len(prompt)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "stream": False,
            "options": {
                "num_predict": 1024,  # Reduced for speed (was 1500)
                "top_k": 30,
                "top_p": 0.85,
                "num_ctx": 3072,  # Reduced context for speed (was 4096)
                "num_thread": 6
            }
        }
        
        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"Sending request to {self.base_url}/api/generate (attempt {attempt + 1}/{max_retries + 1})")
                resp = self.session.post(
                    f"{self.base_url}/api/generate", 
                    json=payload, 
                    timeout=timeout,
                    headers=self.headers
                )
                resp.raise_for_status()
                data = resp.json()
                # Ollama returns response in 'response' field
                if isinstance(data, dict):
                    result = data.get("response") or data.get("text") or data.get("result") or data.get("output") or ""
                    duration = time.time() - start_time
                    response_length = len(result)
                    logger.info(f"Response received - Length: {response_length} chars in {duration:.2f}s")
                    
                    # Log to metrics if available
                    try:
                        import sys
                        if 'main' in sys.modules:
                            metrics = sys.modules['main'].metrics
                            metrics.log_llm_call(self.model, prompt_length, response_length, duration, True)
                    except Exception as e:
                        logger.debug(f"Metrics logging skipped: {e}")
                    
                    return result
                return str(data)
            except requests.exceptions.Timeout as e:
                duration = time.time() - start_time
                if attempt < max_retries:
                    logger.warning(f"Timeout after {duration:.2f}s, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(2)
                    continue
                else:
                    error_msg = f"[OLLAMA_TIMEOUT] Max retries exceeded after {duration:.2f}s"
                    logger.error(error_msg)
                    try:
                        import sys
                        if 'main' in sys.modules:
                            metrics = sys.modules['main'].metrics
                            metrics.log_llm_call(self.model, prompt_length, 0, duration, False)
                            metrics.log_error("TIMEOUT_ERROR", error_msg, "OllamaLLM.generate")
                    except Exception as e:
                        logger.debug(f"Metrics error logging skipped: {e}")
                    return f"Error: LLM timeout after {duration:.2f}s. Please try with a smaller query or simpler task."
            except Exception as e:
                error_msg = f"[OLLAMA_ERROR] {e}"
                duration = time.time() - start_time
                logger.error(error_msg)
            
            # Log error to metrics if available
            try:
                import sys
                if 'main' in sys.modules:
                    metrics = sys.modules['main'].metrics
                    metrics.log_llm_call(self.model, prompt_length, 0, duration, False)
                    metrics.log_error("LLM_ERROR", str(e), "OllamaLLM.generate")
            except Exception as ex:
                logger.debug(f"Metrics error logging skipped: {ex}")
            
            return error_msg

    async def acall(self, messages, **kwargs):
        """Async implementation of call."""
        if isinstance(messages, list):
            prompt = "\n".join([m.get("content", "") if isinstance(m, dict) else str(m) for m in messages])
        else:
            prompt = str(messages)
        return await self.agenerate(prompt, **kwargs)

    async def agenerate(self, prompt: str, timeout: int = 120, max_retries: int = 1, **kwargs):
        """Async generation using aiohttp."""
        logger.info(f"Generating response from Ollama (Async) - Model: {self.model}")
        start_time = time.time()
        prompt_length = len(prompt)
        
        if prompt_length > 6000:
            prompt = prompt[:6000] + "\n[Truncated - provide key details]"
            prompt_length = len(prompt)
            
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "stream": False,
            "options": {
                "num_predict": 1024,
                "top_k": 30,
                "top_p": 0.85,
                "num_ctx": 3072,
                "num_thread": 6
            }
        }
        
        async with aiohttp.ClientSession() as session:
            for attempt in range(max_retries + 1):
                try:
                    async with session.post(
                        f"{self.base_url}/api/generate", 
                        json=payload, 
                        timeout=timeout,
                        headers=self.headers
                    ) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        
                        if isinstance(data, dict):
                            result = data.get("response") or data.get("text") or data.get("result") or data.get("output") or ""
                            duration = time.time() - start_time
                            response_length = len(result)
                            logger.info(f"Async Response received - Length: {response_length} chars in {duration:.2f}s")
                            
                            try:
                                import sys
                                if 'main' in sys.modules:
                                    metrics = sys.modules['main'].metrics
                                    metrics.log_llm_call(self.model, prompt_length, response_length, duration, True)
                            except Exception:
                                pass
                            
                            return result
                        return str(data)
                except Exception as e:
                    duration = time.time() - start_time
                    if attempt < max_retries:
                        logger.warning(f"Async Timeout/Error after {duration:.2f}s, retrying... ({attempt + 1}/{max_retries})")
                        await asyncio.sleep(1)
                        continue
                    else:
                        error_msg = f"[OLLAMA_ASYNC_ERROR] {e}"
                        logger.error(error_msg)
                        return error_msg

# Direct Ollama LLM instantiation with optimized settings
llm = OllamaLLM(temperature=0.1)  # Lower temperature for faster, more focused responses

# Classifier
case_type_classifier = Agent(
    role="Legal Case Classifier",
    goal="Quickly classify as 'civil' or 'criminal'.",
    backstory="""Senior Legal Analyst. Analyze and classify efficiently.

INPUT: User's legal narrative
OUTPUT JSON: {"classification": "civil"|"criminal", "confidence_score": 0-100, "rationale": "brief", "key_signals": ["s1", "s2", "s3"]}

Be decisive. Choose most probable. List 3 indicators.""",
    verbose=False,
    llm=llm
)

# Civil Agents
civil_fact_interpreter = Agent(
    role="Civil Fact Interpreter",
    goal="Extract structured facts from the narrative for civil litigation.",
    backstory="""
You are a Specialist in family, property, and contractual disputes under Indian law.
Your job is to parse the narrative into structured data usable for legal analysis.

YOU WILL RECEIVE:
1. User's raw narrative.
2. Classification result (Civil).

YOUR OUTPUT FORMAT (JSON):
{
    "parties": [{"role": "Plaintiff/Defendant", "name": "Name/Description"}],
    "dates": [{"event": "Event Description", "date": "Date/Time", "inferred": boolean}],
    "claims": ["Relief sought 1", "Relief sought 2"],
    "evidence": ["Document/Proof 1", "Document/Proof 2"],
    "uncertainties": ["Ambiguity 1", "Ambiguity 2"],
    "derivation_notes": "Brief explanation of how facts were derived."
}

IMPORTANT QUALITY STANDARDS:
- Aim for precise, short JSON output.
- Infer dates where possible but mark them as inferred.
- List specific relief sought (e.g., damages, injunction).
""",
    verbose=True,
    llm=llm
)

civil_law_mapper = Agent(
    role="Civil Law Mapper",
    goal="Map extracted facts to relevant Indian civil statutes and procedural rules.",
    backstory="""
You are an Expert in Indian civil statutes, limitation periods, and court jurisdiction.
Your task is to identify the specific laws that apply to the structured facts.

YOU WILL RECEIVE:
1. Structured facts from Civil Fact Interpreter.

YOUR OUTPUT FORMAT (PRIORITIZED LIST):
1. **[Statute Name & Section]**
   - **Applicability**: Plain-English explanation of why it applies.
   - **Key Provisions**: Limitation periods, remedies, jurisdiction.
2. **[Next Statute...]**
...

IMPORTANT QUALITY STANDARDS:
- Prioritize practical remedies and exact section citations.
- Explain *why* a section applies to the specific facts.
- Note any limitation bar issues immediately.
""",
    verbose=True,
    llm=llm
)

civil_precedent_finder = Agent(
    role="Civil Precedent Finder",
    goal="Find relevant civil judgments to support the legal analysis.",
    backstory="""
You are a Legal Researcher knowledgeable in landmark civil cases (Supreme Court/High Court).
Your goal is to find precedents that strengthen the user's position or clarify the law.

YOU WILL RECEIVE:
1. Structured facts.
2. Applicable laws.

YOUR OUTPUT FORMAT (CASE LIST):
1. **[Case Name]** (Citation, Year, Court)
   - **Headnote**: Short summary of the case.
   - **Holding**: One-sentence legal ruling.
   - **Relevance**: 2 sentences on how this maps to the user's facts.
   - **Distinction**: Any limits to the analogy.

IMPORTANT QUALITY STANDARDS:
- Focus on precedents affecting remedies and procedure.
- Cite real cases where possible (or highly probable landmark cases).
- Explain the connection to the current facts clearly.
""",
    verbose=True,
    llm=llm
)

# Criminal Agents
criminal_fact_interpreter = Agent(
    role="Criminal Fact Interpreter",
    goal="Extract structured facts from the narrative for criminal proceedings.",
    backstory="""
You are a Former Public Prosecutor skilled in IPC fact-pattern recognition.
Your job is to identify elements of crimes and immediate safety concerns.

YOU WILL RECEIVE:
1. User's raw narrative.
2. Classification result (Criminal).

YOUR OUTPUT FORMAT (JSON):
{
    "offenses": ["Suspected IPC Section 1", "Suspected IPC Section 2"],
    "accused": [{"identity": "Name/Desc", "role": "Role"}],
    "injuries": ["Injury 1", "Injury 2"],
    "threats": ["Threat detail"],
    "location": "Incident Location",
    "dates": ["Date/Time of incident"],
    "evidence": ["Witnesses", "Medical Reports", "Digital Evidence"],
    "safety_alert": "High/Medium/Low",
    "immediate_actions": ["Action 1", "Action 2"]
}

IMPORTANT QUALITY STANDARDS:
- Provide concise, actionable outputs.
- Highlight any immediate physical threats.
- Identify specific IPC offenses suggested by facts.
""",
    verbose=True,
    llm=llm
)

criminal_law_mapper = Agent(
    role="Criminal Law Mapper",
    goal="Map facts to IPC sections and outline criminal procedure.",
    backstory="""
You are an Expert in Indian Penal Code (IPC) and Code of Criminal Procedure (CrPC).
Your task is to detail the legal framework for the identified offenses.

YOU WILL RECEIVE:
1. Structured criminal facts.

YOUR OUTPUT FORMAT (LEGAL ANALYSIS):
1. **[IPC Section]**
   - **Elements**: What constitutes this crime.
   - **Fact Mapping**: How the user's facts meet these elements.
   - **Nature**: Cognizable/Non-cognizable, Bailable/Non-bailable.
2. **Procedural Steps**:
   - Immediate steps (FIR, Medical Exam).
   - Arrest and Bail provisions.
   - Timing constraints (Limitation).

IMPORTANT QUALITY STANDARDS:
- Prioritize survivor safety and immediate legal remedies.
- Clearly distinguish between cognizable and non-cognizable offenses.
- Explain the FIR process relevant to the specific crimes.
""",
    verbose=True,
    llm=llm
)

criminal_precedent_finder = Agent(
    role="Criminal Precedent Finder",
    goal="Locate criminal judgments relevant to the offense and procedure.",
    backstory="""
You are a Researcher focused on precedents for assault, theft, harassment, and fraud.
Your goal is to find cases that clarify elements, sentencing, or procedural relief.

YOU WILL RECEIVE:
1. Criminal facts.
2. Identified IPC sections.

YOUR OUTPUT FORMAT (CASE LIST):
1. **[Case Name]** (Citation, Year)
   - **Holding**: Short legal ruling.
   - **Relevance**: How it applies to the user's specific situation.
   - **Statutory Interpretation**: Notes on how the court interpreted the section.

IMPORTANT QUALITY STANDARDS:
- Emphasize cases affecting sentencing or procedural relief (e.g., anticipatory bail).
- Ensure relevance to the specific type of offense.
""",
    verbose=True,
    llm=llm
)

# Shared Agents
constitutional_validator = Agent(
    role="Constitutional Validator",
    goal="Assess potential constitutional violations (Articles 14, 15, 19, 21).",
    backstory="""
You are a Constitutional Law Expert focused on fundamental rights.
Your task is to check if the situation involves violations of basic rights.

YOU WILL RECEIVE:
1. Fact patterns (Civil or Criminal).
2. Legal mapping.

YOUR OUTPUT FORMAT (CONSTITUTIONAL CHECK):
- **Article Flagged**: [Article Number]
  - **Rationale**: Legal reasoning for the violation.
  - **Remedy**: Writ petition possibilities (Habeas Corpus, Mandamus, etc.).
  - **Non-Applicability**: If no constitutional issue, explain why briefly.

IMPORTANT QUALITY STANDARDS:
- Provide plain-language explanations suitable for non-lawyers.
- Focus on Articles 14 (Equality), 15 (Non-discrimination), 19 (Freedoms), 21 (Life/Liberty).
""",
    verbose=True,
    llm=llm
)

legal_pathway_advisor = Agent(
    role="Legal Pathway Advisor",
    goal="Create a practical, time-bound action plan for the user.",
    backstory="""
You are a Legal Aid Counselor experienced in guiding clients through the Indian court system.
Your goal is to translate legal analysis into a step-by-step guide.

YOU WILL RECEIVE:
1. Full legal analysis (Facts, Laws, Precedents).

YOUR OUTPUT FORMAT (ACTION PLAN):
1. **Step 1: [Action Name]** (Timeline: X Days)
   - **Details**: What to do exactly.
   - **Forms/Documents**: What is needed.
   - **Cost Estimate**: Low/Medium/High.
2. **Step 2...**
...
**Templates**:
- [Short template for Letter/FIR/Complaint]

IMPORTANT QUALITY STANDARDS:
- Make steps practical and low-barrier.
- Include specific timelines (e.g., "File within 24 hours").
- Provide simple templates for immediate use.
""",
    verbose=True,
    llm=llm
)

report_synthesizer = Agent(
    role="Victim-Friendly Report Synthesizer",
    goal="Synthesize all analysis into a comprehensive, easy-to-understand legal report.",
    backstory="""
You are a Senior Legal Synthesizer who converts complex legal analysis into accessible guidance.
Your job is to combine outputs from all agents into one coherent report for the user.

YOU WILL RECEIVE:
1. Case Classification.
2. Fact Interpretation.
3. Law Mapping.
4. Precedents.
5. Constitutional Analysis.
6. Action Plan.

YOUR OUTPUT FORMAT (FINAL REPORT):
---
**LEGAL GUIDANCE REPORT**

**Case Type**: [Civil/Criminal]
**Date**: [Current Date]

**EXECUTIVE SUMMARY**
[Brief overview of the situation and key legal standing]

**1. KEY FACTS**
[Structured summary of events, parties, and evidence]

**2. APPLICABLE LAWS & SECTIONS**
[List of laws with plain-English explanations of why they apply]

**3. RELEVANT PRECEDENTS**
[Key cases that support the user's position]

**4. CONSTITUTIONAL ASPECTS**
[Any fundamental rights issues]

**5. RECOMMENDED NEXT STEPS**
[The step-by-step action plan]

**6. TEMPLATES & TOOLS**
[Drafts for letters/FIRs]

**7. TIMELINES & OUTCOMES**
[Estimated duration and potential results]

**8. DISCLAIMER**
[Standard legal disclaimer]
---

IMPORTANT QUALITY STANDARDS:
- Use simple language; avoid excessive legalese.
- Ensure the tone is empathetic but professional.
- Make the "Next Steps" section the most prominent and actionable.
- Verify consistency across sections.
""",
    verbose=True,
    llm=llm
)

# Export
CIVIL_AGENTS = [civil_fact_interpreter, civil_law_mapper, civil_precedent_finder]
CRIMINAL_AGENTS = [criminal_fact_interpreter, criminal_law_mapper, criminal_precedent_finder]
SHARED_AGENTS = [constitutional_validator, legal_pathway_advisor, report_synthesizer]
CLASSIFIER_AGENT = case_type_classifier