# MALJRS - Multi-Agent Legal Justice Recommendation System

This project consists of three main components that must be running simultaneously:
1.  **Ollama (AI Service)**: Provides local LLM capabilities.
2.  **Backend (FastAPI)**: Python API server that orchestrates AI agents.
3.  **Frontend (React)**: User interface.

## Prerequisites
-   [Ollama](https://ollama.com) installed.
-   Python 3.11+ installed.
-   Node.js 18+ installed.

## Quick Start Guide

You will need **3 separate terminal windows**.

### 1. Start AI Service (Terminal 1)
This runs the local LLM server.
```powershell
ollama serve
```
*Keep this terminal open.*

### 2. Start Backend API (Terminal 2)
This runs the Python server.
```powershell
cd Backend
# Activate virtual environment (if not already active)
# .venv\Scripts\activate

# Install dependencies (only needed once)
# pip install -r requirements.txt

# Start the server
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```
*Wait for "Application startup complete".*

### 3. Start Frontend UI (Terminal 3)
This runs the web interface.
```powershell
cd Frontend
# Install dependencies (only needed once)
# npm install

# Start the dev server
npm run dev
```
*Open your browser to the URL shown (usually http://localhost:5173).*
