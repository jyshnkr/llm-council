# CLAUDE.md - LLM Council Quick Reference

**LLM Council**: 3-stage deliberation system. Stage 1: parallel responses. Stage 2: anonymized peer ranking. Stage 3: chairman synthesis.

**Tech Stack**: Python/FastAPI (port 8001) + React/Vite (5173). OpenRouter API via `OPENROUTER_API_KEY`.

## Quick Navigation

- **Architecture**: See `.claude/memory/architecture.md` (system design, data flow, core modules)
- **Code Style**: See `.claude/memory/conventions.md` (backend/frontend patterns, configuration)
- **Glossary**: See `.claude/memory/glossary.md` (key terms, Stage 1-3 definitions)

## Critical Implementation Notes

**Backend Modules** (`backend/`):

- `config.py`: `COUNCIL_MODELS`, `CHAIRMAN_MODEL`, OpenRouter key
- `council.py`: `stage1_collect_responses()`, `stage2_collect_rankings()`, `stage3_synthesize_final()`
- `openrouter.py`: `query_models_parallel()` (async, graceful degradation)
- `storage.py`: JSON storage in `data/conversations/`
- `main.py`: FastAPI on port 8001, CORS for localhost:5173 + 3000

**Frontend** (`frontend/src/`):

- `App.jsx`: Conversation orchestration
- `Stage1.jsx`, `Stage2.jsx`, `Stage3.jsx`: Tab-based display
- `api.js`: API_BASE = '<http://localhost:8001>'
- Styling: Light mode, `#4a90e2` blue, markdown wrapped in `.markdown-content`

**Stage 2 Anonymization**:

- Models see: "Response A", "Response B", etc.
- Backend creates: `label_to_model = {"Response A": "openai/gpt-5.1", ...}`
- Frontend de-anonymizes client-side for display
- Format: "FINAL RANKING:" + numbered list, no extra text

**Critical**:

1. Run backend as `python -m backend.main` (relative imports required)
2. ALL ReactMarkdown wrapped in `<div className="markdown-content">`
3. Metadata (label_to_model, aggregate_rankings) is ephemeral, not persisted

## Common Issues

- **Import errors**: Use relative imports, run from project root
- **CORS errors**: Check `main.py` allowed origins match frontend
- **Ranking parse failures**: Fallback regex handles malformed output
