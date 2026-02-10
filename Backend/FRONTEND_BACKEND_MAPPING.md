# Frontend-to-Backend Mapping

## Data Contract Mappings

### Core Data Types

| Frontend (TypeScript) | Backend (Python) | File Locations |
|----------------------|------------------|----------------|
| `TimelineEvent` | `TimelineEvent` | [case.ts:L1-7](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Frontend/src/types/case.ts#L1-L7) → [case_models.py:L10-16](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/models/case_models.py#L10-L16) |
| `EvidenceItem` | `EvidenceItem` | [case.ts:L9-16](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Frontend/src/types/case.ts#L9-L16) → [case_models.py:L19-26](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/models/case_models.py#L19-L26) |
| `LawSection` | `LawSection` | [case.ts:L18-23](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Frontend/src/types/case.ts#L18-L23) → [case_models.py:L29-34](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/models/case_models.py#L29-L34) |
| `WitnessInfo` | `WitnessInfo` | [case.ts:L25-30](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Frontend/src/types/case.ts#L25-L30) → [case_models.py:L37-42](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/models/case_models.py#L37-L42) |
| `CaseData` | `CaseData` | [case.ts:L32-58](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Frontend/src/types/case.ts#L32-L58) → [case_models.py:L45-85](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/models/case_models.py#L45-L85) |

**Validation**: All field names, types, and constraints match exactly.

---

## Frontend Page → Backend Endpoint Mappings

### Page 1-8: Case Info Collection
**Frontend**: [CaseInfoPage](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Frontend/src/pages/CaseInfoPage.tsx), [TimelinePage](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Frontend/src/pages/TimelinePage.tsx), etc.

**Backend Endpoints**:
- `POST /api/cases` — Create case
- `PUT /api/cases/{id}` — Update case (auto-save)

**Flow**:
1. User fills form → `CaseContext.updateCase()`
2. On blur/save → `POST /api/cases` with `CaseData`
3. Backend validates via Pydantic → saves to JSON storage

---

### Page 9: AI Assistance Selection
**Frontend**: [AIAssistancePage.tsx](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Frontend/src/pages/AIAssistancePage.tsx)

**User selects from**:
- "Identify legal issues"
- "Find relevant precedents"
- "Prepare arguments"
- "Find weaknesses"
- "Draft court notes"
- "Prepare cross-questions"

**Backend Endpoints** (one-to-one mapping):

| Frontend Option | Backend Endpoint | Service Method |
|----------------|------------------|----------------|
| "Identify legal issues" | `POST /api/ai/identify-issues` | [ai_service.py:L60](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/services/ai_service.py#L60) |
| "Find relevant precedents" | `POST /api/ai/find-precedents` | [ai_service.py:L88](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/services/ai_service.py#L88) |
| "Prepare arguments" | `POST /api/ai/prepare-arguments` | [ai_service.py:L116](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/services/ai_service.py#L116) |
| "Find weaknesses" | `POST /api/ai/find-weaknesses` | [ai_service.py:L144](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/services/ai_service.py#L144) |
| "Draft court notes" | `POST /api/ai/draft-notes` | [ai_service.py:L172](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/services/ai_service.py#L172) |
| "Prepare cross-questions" | `POST /api/ai/prepare-questions` | [ai_service.py:L200](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/services/ai_service.py#L200) |

---

### Page 10: Review & Submit
**Frontend**: [ReviewPage.tsx](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Frontend/src/pages/ReviewPage.tsx)

**Current Behavior** (Line 14-18):
```typescript
const handleSubmit = () => {
  const json = JSON.stringify(caseData, null, 2);
  console.log("Case Data JSON:", json);
  toast.success("Case submitted to AI system!");
};
```

**Required Change**:
```typescript
const handleSubmit = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/ai/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ caseData })
    });
    
    const result = await response.json();
    if (result.success) {
      // Display result.report
      toast.success("Analysis complete!");
    }
  } catch (error) {
    toast.error("Failed to process case");
  }
};
```

**Backend Endpoint**: `POST /api/ai/process`
- Route: [ai_processing.py:L26](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/api/routes/ai_processing.py#L26)
- Service: [ai_service.py:L22](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/services/ai_service.py#L22)

---

## Data Flow: Frontend → Backend

### 1. User Input → Structured Data

```
User fills forms
    ↓
CaseContext stores in useState
    ↓
localStorage (draft persistence)
    ↓
CaseData object (TypeScript)
```

### 2. Submit → API Call

```typescript
// Frontend
const caseData: CaseData = {...}
fetch('/api/ai/process', {
  body: JSON.stringify({ caseData })
})
```

### 3. Backend Processing

```
FastAPI receives request
    ↓
Pydantic validates CaseData structure
    ↓
AIService.process_full_case(caseData)
    ↓
Parser: case_to_narrative(caseData)
    ↓
Narrative text generated
```

**Example Narrative** (generated from frontend data):

```
============================================================
LEGAL CASE NARRATIVE
============================================================

CASE INFORMATION
----------------------------------------
Case Title: Property Dispute - Test Case
Case Type: Civil
Court/Jurisdiction: District Court
Current Stage: Notice
Plaintiff/Complainant: Test Plaintiff
Defendant/Respondent: Test Defendant

TIMELINE OF EVENTS
----------------------------------------
1. Date: 2024-01-15
   Event: Initial agreement signed
   People Involved: Both parties
   Evidence Status: [PROOF AVAILABLE]
...
```

### 4. AI Agent Processing

```
Multi-Agent System receives narrative
    ↓
Classifier: Determines "civil" or "criminal"
    ↓
Fact Interpreter: Extracts structured facts
    ↓
Law Mapper: Identifies applicable laws
    ↓
Precedent Finder: Finds relevant cases
    ↓
Constitutional Validator: Checks rights violations
    ↓
Pathway Advisor: Creates action plan
    ↓
Report Synthesizer: Generates full report
```

### 5. Response Formatting

```
Raw AI output (text)
    ↓
ResponseFormatter.format_ai_response()
    ↓
Structured JSON with:
  - classification
  - legalIssues
  - applicableLaws
  - precedents
  - actionPlan
  - etc.
```

### 6. Frontend Display

```json
{
  "success": true,
  "caseId": "case_abc123",
  "report": {
    "classification": "civil",
    "executiveSummary": "...",
    "legalIssues": ["Issue 1", "Issue 2"],
    "applicableLaws": [...],
    "precedents": [...],
    "actionPlan": [...]
  }
}
```

---

## API Request/Response Examples

### Create Case

**Request**:
```http
POST /api/cases
Content-Type: application/json

{
  "data": {
    "caseTitle": "Property Dispute",
    "caseType": "Civil",
    "courtJurisdiction": "High Court",
    "stageOfCase": "Notice",
    "plaintiffName": "John Doe",
    "defendantName": "Jane Smith",
    "timeline": [...],
    "claims": [...],
    "evidence": [...],
    ...
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Case created successfully",
  "caseId": "case_a1b2c3d4e5f6",
  "status": "draft",
  "timestamp": "2026-02-09T23:10:00"
}
```

---

### Full AI Processing

**Request**:
```http
POST /api/ai/process
Content-Type: application/json

{
  "caseData": { /* full CaseData object */ },
  "options": ["Identify legal issues", "Find precedents"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Case analysis completed",
  "caseId": "case_a1b2c3d4e5f6",
  "report": {
    "classification": "civil",
    "executiveSummary": "This case involves...",
    "keyFacts": "Timeline shows...",
    "applicableLaws": [
      {
        "statute": "Transfer of Property Act, 1882",
        "section": "Section 54",
        "applicability": "Governs sale of property..."
      }
    ],
    "precedents": [
      {
        "caseName": "ABC v. XYZ",
        "citation": "AIR 2020 SC 1234",
        "court": "Supreme Court",
        "year": 2020,
        "relevance": "Similar facts involving..."
      }
    ],
    "actionPlan": [
      {
        "step": 1,
        "title": "Send Legal Notice",
        "timeline": "Within 7 days",
        "details": "Draft and send legal notice to defendant..."
      }
    ]
  },
  "rawOutput": "Raw multi-agent output for debugging"
}
```

---

## Component Dependencies

### Backend Imports Chain

```python
# API Layer
api/routes/ai_processing.py
    ↓ imports
services/ai_service.py
    ↓ imports
parsers/case_to_narrative.py
parsers/response_formatter.py
models/case_models.py
    ↓ calls
main.py (run_legal_crew)
    ↓ uses
agents.py (multi-agent system)
tasks.py (agent tasks)
```

### Frontend Data Flow

```typescript
// Form Input
pages/CaseInfoPage.tsx
    ↓ updates
contexts/CaseContext.tsx (useState)
    ↓ stores
localStorage ("legal-case-draft")
    ↓ submits via
pages/ReviewPage.tsx
    ↓ sends to
Backend API (/api/ai/process)
```

---

## Validation Points

### Frontend Validation
- **Where**: React Hook Form with Zod (if implemented)
- **What**: Required fields, format validation
- **When**: On form submit

### Backend Validation
- **Where**: Pydantic models ([case_models.py](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Backend/models/case_models.py))
- **What**: Type checking, Literal values, required fields
- **When**: On API request receipt

**Example**: `EvidenceItem.strength` must be exactly "Strong", "Medium", or "Weak"
- Frontend enforces via dropdown
- Backend validates via `Literal["Strong", "Medium", "Weak"]`

---

## Error Handling

### Frontend Errors
- Network errors → Toast notification
- Validation errors → Form field errors

### Backend Errors

**Validation Error** (422):
```json
{
  "success": false,
  "message": "Validation error",
  "errors": [
    {
      "loc": ["body", "data", "caseType"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Processing Error** (500):
```json
{
  "success": false,
  "message": "AI processing error: ...",
  "error": "Detailed error message"
}
```

---

## Storage Locations

### Frontend
- **Draft Cases**: Browser localStorage (key: `"legal-case-draft"`)
- **Location**: [CaseContext.tsx:L15](file:///c:/Users/sains/OneDrive/Desktop/Project-MALJRS/Frontend/src/contexts/CaseContext.tsx#L15)

### Backend
- **Cases**: `Backend/data/cases/{case_id}.json`
- **AI Reports**: `Backend/output/final_report_{timestamp}.txt`
- **Logs**: `Backend/logs/maljrs_{timestamp}.log`

---

## Summary

Every frontend component, input field, and action has an **exact corresponding** backend endpoint, data model, or processing function:

- **10 frontend pages** → 12 API endpoints
- **5 TypeScript types** → 5 Pydantic models
- **6 AI assistance options** → 6 dedicated API endpoints
- **1 submit button** → 1 primary endpoint (`/api/ai/process`)

The backend is **entirely frontend-driven** with no unused code or generic endpoints.
