# MALJRS Backend API

## Overview

Frontend-driven REST API for the Multi-Agent Legal Justice Recommendation System. This backend strictly serves the frontend's 10-step legal case workflow with structured JSON API endpoints.

## Quick Start

### 1. Install Dependencies

```bash
cd Backend
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
cd Backend
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

API Documentation: `http://localhost:8000/api/docs`

### 3. Start Frontend

In a separate terminal:

```bash
cd Frontend
npm run dev
```

Frontend will connect to the backend API automatically.

## API Endpoints

### Case Management

- `POST /api/cases` - Create new case
- `GET /api/cases/{case_id}` - Get case details
- `PUT /api/cases/{case_id}` - Update case
- `DELETE /api/cases/{case_id}` - Delete case
- `GET /api/cases` - List all cases

### AI Processing

All endpoints accept `CaseData` and return structured results:

- `POST /api/ai/process` - Full case analysis (primary endpoint)
- `POST /api/ai/identify-issues` - Identify legal issues
- `POST /api/ai/find-precedents` - Find precedents  
- `POST /api/ai/prepare-arguments` - Prepare arguments
- `POST /api/ai/find-weaknesses` - Find weaknesses
- `POST /api/ai/draft-notes` - Draft court notes
- `POST /api/ai/prepare-questions` - Cross-examination questions

## Architecture

```
Backend/
├── api/                    # REST API layer
│   ├── app.py             # FastAPI application
│   ├── routes/
│   │   ├── case.py        # Case CRUD endpoints
│   │   └── ai_processing.py  # AI endpoints
│   └── middleware/
│       ├── cors.py        # CORS configuration
│       └── error_handler.py  # Error handling
├── models/                 # Data models (Pydantic)
│   ├── case_models.py     # CaseData matching frontend
│   ├── request_models.py  # API request schemas
│   └── response_models.py # API response schemas
├── parsers/               # Data transformation
│   ├── case_to_narrative.py   # Struct → narrative
│   └── response_formatter.py  # AI output → JSON
├── services/              # Business logic
│   ├── case_service.py    # Case management
│   └── ai_service.py      # AI orchestration
├── storage/               # Persistence
│   └── json_storage.py    # JSON file storage
├── agents.py              # Multi-agent system
├── tasks.py               # Agent tasks
└── main.py                # CLI interface (secondary)
```

## Frontend-Backend Contract

All data models in `models/case_models.py` **exactly match** frontend TypeScript types in `Frontend/src/types/case.ts`.

**Example**: Frontend `CaseData` interface → Backend `CaseData` Pydantic model

This ensures type safety and validation across the stack.

## How It Works

1. **Frontend** collects structured data through 10-step workflow
2. **API** receives `CaseData` via REST endpoints
3. **Parser** converts structured data → natural language narrative
4. **AI Service** processes narrative through multi-agent system
5. **Formatter** structures AI output → JSON response
6. **Frontend** displays results

## Testing

### Manual Testing

```bash
# Health check
curl http://localhost:8000/api/health

# Create case
curl -X POST http://localhost:8000/api/cases \
  -H "Content-Type: application/json" \
  -d @test_case.json
```

### Interactive API Docs

Visit `http://localhost:8000/api/docs` for Swagger UI with interactive testing.

## Configuration

Environment variables (create `.env` file):

```env
OLLAMA_BASE_URL=https://ollama.com
OLLAMA_MODEL=gpt-oss:120b
OLLAMA_API_KEY=your_api_key_here
TEMPERATURE=0.1
```

## Troubleshooting

**ImportError: No module named 'fastapi'**
- Run: `pip install -r requirements.txt`

**CORS errors in browser**
- Check frontend URL in `api/middleware/cors.py`
- Default: `http://localhost:5173`

**AI processing fails**
- Ensure Ollama is configured in `.env`
- Check `Backend/logs/` for detailed error logs

## Key Design Principles

✅ **Frontend-Driven**: Every endpoint exists because frontend needs it  
✅ **Strict Contracts**: Request/response schemas match frontend exactly  
✅ **Intelligent Parsing**: Structured data → narrative conversion  
✅ **Clean Architecture**: Routes → Services → Parsers → Agents  
✅ **No Redundancy**: Only necessary endpoints, no generic APIs
