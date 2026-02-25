# Architecture & System Design

## Project Overview
**LLM Council** is a 3-stage deliberation system where multiple LLMs collaboratively answer user questions with anonymized peer review, preventing models from playing favorites.

**Type**: Full-stack web application
**Stack**: Python/FastAPI (backend) + React/Vite (frontend)
**Key Innovation**: Anonymized ranking in Stage 2 for unbiased peer evaluation

## Core Data Flow

```
User Query
    ↓
Stage 1: Parallel queries → [individual responses from council models]
    ↓
Stage 2: Anonymize → Parallel ranking queries → [evaluations + parsed rankings]
    ↓
Aggregate Rankings Calculation → [sorted by avg position]
    ↓
Stage 3: Chairman synthesis with full context
    ↓
Return: {stage1, stage2, stage3, metadata}
    ↓
Frontend: Display with tabs + validation UI
```

## Backend Architecture

### FastAPI Application (`backend/main.py`)
- **Port**: 8001 (changed from 8000 to avoid conflicts)
- **CORS**: Enabled for `localhost:5173` and `localhost:3000`
- **Key Endpoints**:
  - `POST /api/conversations` - Create conversation
  - `GET /api/conversations` - List conversations
  - `GET /api/conversations/{id}` - Get conversation
  - `POST /api/conversations/{id}/message` - Send message with full output
  - `POST /api/conversations/{id}/message/stream` - Streaming response

### Core Modules

**`config.py`**
- `COUNCIL_MODELS` - List of OpenRouter model identifiers
- `CHAIRMAN_MODEL` - Model that synthesizes final answer
- Uses `OPENROUTER_API_KEY` from `.env`

**`openrouter.py`**
- `query_model()` - Single async model query
- `query_models_parallel()` - Parallel queries using `asyncio.gather()`
- Graceful degradation: returns None on failure, continues with successful responses

**`council.py`** - Core 3-stage orchestration
- `stage1_collect_responses()` - Parallel queries to council models
- `stage2_collect_rankings()` - Anonymizes responses, gets rankings, parses output
- `stage3_synthesize_final()` - Chairman synthesis
- `calculate_aggregate_rankings()` - Computes average rank position
- `parse_ranking_from_text()` - Extracts "FINAL RANKING:" section

**`storage.py`**
- JSON-based storage in `data/conversations/`
- Structure: `{id, created_at, messages[]}`
- Assistant messages contain: `{role, stage1, stage2, stage3}`

## Frontend Architecture

**React Components** (`frontend/src/components/`)
- `ChatInterface.jsx` - Multiline textarea, Enter-to-send, Shift+Enter for newline
- `Stage1.jsx` - Tab view of individual model responses
- `Stage2.jsx` - Raw evaluations + de-anonymized display + aggregate rankings
- `Stage3.jsx` - Final synthesized answer (green-tinted background)
- `Sidebar.jsx` - Conversation list

**API Client** (`frontend/src/api.js`)
- `listConversations()` - Fetch all conversations
- `createConversation()` - Create new conversation
- `sendMessage()` - Standard request/response
- `sendMessageStream()` - Server-Sent Events for progressive updates

## Key Design Decisions

### Anonymization Strategy (Stage 2)
- Models receive: "Response A", "Response B", etc.
- Backend creates `label_to_model` mapping
- Frontend de-anonymizes client-side for display
- Models see anonymous labels only (prevents bias)

### Stage 2 Prompt Format
```
1. Evaluate each response individually first
2. Provide "FINAL RANKING:" header
3. Numbered list format: "1. Response C", "2. Response A", etc.
4. No additional text after ranking section
```
Ensures parseable output + thoughtful evaluation.

### Error Handling
- Graceful degradation: continue with successful responses if some fail
- Never fail entire request due to single model failure
- Log errors internally

### Metadata Management
- Returns in API response: `{label_to_model, aggregate_rankings}`
- NOT persisted to JSON storage (ephemeral, computed on request)
- Frontend stores for display in current session

## Critical Implementation Details

### Module Imports
- All backend modules use relative imports: `from .config import ...`
- Critical for Python's module system when running `python -m backend.main`

### Frontend Styling
- Light mode theme, primary color: `#4a90e2` (blue)
- All ReactMarkdown wrapped in `<div className="markdown-content">` for 12px padding
- Green background `#f0fff0` for Stage 3 (conclusion emphasis)

## SEARCH KEYWORDS
`fastapi`, `3-stage deliberation`, `anonymized peer review`, `asyncio parallel queries`, `openrouter`, `json storage`, `react tabs`, `ranking aggregation`, `de-anonymization`
