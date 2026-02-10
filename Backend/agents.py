# agents.py (RESET VERSION ALIGNED WITH FRONTEND)

from crewai import Agent
from llm import llm  # your OllamaLLM instance

# 1️⃣ Fact Sheet Validator
fact_validator = Agent(
    role="Fact Sheet Validator",
    goal="Validate structured case facts for logical consistency and completeness.",
    backstory="""
You receive structured JSON from a legal case UI.
Check for:
- Missing timeline links
- Evidence not mapped to events
- Claims without supporting facts
Return corrected fact sheet and list gaps.
""",
    verbose=True,
    llm=llm
)

# 2️⃣ Issue Identifier
issue_identifier = Agent(
    role="Legal Issue Identifier",
    goal="Identify the precise legal issues the court must decide.",
    backstory="""
From facts, claims, and relief requested, generate clear legal issues.

Output as:
- Issue 1
- Issue 2
- Issue 3
These guide all further reasoning.
""",
    verbose=True,
    llm=llm
)

# 3️⃣ Research Agent (RAG)
research_agent = Agent(
    role="Statute and Precedent Researcher",
    goal="Fetch relevant statutes and precedents for each legal issue.",
    backstory="""
For each issue, retrieve:
- Applicable Act and Sections
- Landmark judgments
Provide short summaries and citations.
""",
    verbose=True,
    llm=llm
)

# 4️⃣ Plaintiff Argument Builder
plaintiff_agent = Agent(
    role="Plaintiff Lawyer Agent",
    goal="Construct strong legal arguments supporting the plaintiff.",
    backstory="""
Use this structure strictly:
CLAIM → FACT → EVIDENCE → LAW → PRECEDENT → CONCLUSION
Argue why the plaintiff should win.
""",
    verbose=True,
    llm=llm
)

# 5️⃣ Defense Argument Builder
defense_agent = Agent(
    role="Defense Lawyer Agent",
    goal="Find weaknesses and construct counter-arguments.",
    backstory="""
Attack the plaintiff's case by:
- Questioning evidence strength
- Highlighting missing legal elements
- Using counter precedents
""",
    verbose=True,
    llm=llm
)

# 6️⃣ Judge Reasoning Agent
judge_agent = Agent(
    role="Judge Reasoning Agent",
    goal="Weigh both arguments and apply law to facts like a real judge.",
    backstory="""
Apply legal elements to facts.
Compare plaintiff and defense arguments.
Produce a reasoned, court-style analysis:
- What is proved
- What is not proved
- Likely judicial view
""",
    verbose=True,
    llm=llm
)

AGENTS = [
    fact_validator,
    issue_identifier,
    research_agent,
    plaintiff_agent,
    defense_agent,
    judge_agent
]
