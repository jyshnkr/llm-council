# Glossary & Key Terms

## Project-Specific Terms

**Council Models**
- The set of LLMs that participate in Stage 1 and Stage 2
- Defined in `config.COUNCIL_MODELS`
- Each model is identified by OpenRouter identifier (e.g., "openai/gpt-5.1")
- Respond independently in Stage 1, rank in Stage 2

**Chairman Model**
- The single LLM that synthesizes final answer in Stage 3
- Defined in `config.CHAIRMAN_MODEL`
- Receives all Stage 1 responses + aggregated Stage 2 rankings as context
- Can be different from or same as council members

**Anonymization / De-anonymization**
- **Anonymization**: Converting model responses to "Response A", "Response B", etc. before sending to peers for ranking
- **De-anonymization**: Converting labels back to model names for frontend display
- Maps stored in `label_to_model` dict: `{"Response A": "openai/gpt-5.1", ...}`

**Aggregate Rankings**
- Computed ranking scores across all peer evaluations
- Average position of each response across all evaluations
- Example: "Response A: avg position 1.2 (from 5 votes)"
- Used to display confidence in final ranking

**Label**
- Anonymous identifier for a response: "Response A", "Response B", "Response C", etc.
- Used only in Stage 2 prompts to prevent bias
- Mapping discarded after ranking collection (re-anonymized for each query)

## System Architecture Terms

**Stage 1: Collection**
- All council models respond to user query in parallel
- Responses stored independently without interaction
- Output: List of `{model, response}` pairs

**Stage 2: Ranking**
- Each council model evaluates anonymized responses
- Models rank responses by quality/accuracy
- Output: List of `{model, evaluation, parsed_ranking}` + `label_to_model` mapping

**Stage 3: Synthesis**
- Chairman reads all Stage 1 responses + all Stage 2 evaluations + aggregated rankings
- Creates final synthesized answer incorporating peer insights
- Output: Final response text

## Technical Terms

**Graceful Degradation**
- If one model API call fails, others continue successfully
- Entire request doesn't fail due to single model failure
- Partial responses acceptable (better than no response)

**Parsing (Ranking)**
- Extracting "FINAL RANKING:" section from model output
- Format: numbered list "1. Response C", "2. Response A", etc.
- Fallback regex if strict format not followed
- Result: `parsed_ranking = [rank_order]` (e.g., ["C", "A", "B"])

**Label-to-Model Mapping**
- Dict created in Stage 2: `{"Response A": actual_model_id, ...}`
- Used by frontend to display model names in Stage 2 evaluations
- Ephemeral (not persisted, recomputed per request)

**Metadata**
- Returned in API response alongside stage outputs
- Contains: `label_to_model`, `aggregate_rankings`
- Ephemeral (computed, not stored in JSON)

**OpenRouter**
- Third-party LLM API service
- Provides unified interface to multiple model providers (OpenAI, Google, etc.)
- Authentication via `OPENROUTER_API_KEY`

## Frontend Terms

**Markdown Content Wrapper**
- CSS class `.markdown-content` with 12px padding
- Applied to all `<ReactMarkdown>` components
- Prevents cluttered appearance in UI

**Tab View**
- Stage1.jsx: Tabs for each model's response
- Stage2.jsx: Tabs for each model's evaluation
- Interactive switching between responses/evaluations

**Green Conclusion**
- Stage 3 container uses background `#f0fff0` (light green)
- Visually distinguishes final synthesized answer
- Emphasizes conclusion vs. deliberation

## File Structure Terms

**data/conversations/**
- JSON storage directory
- One file per conversation with UUID filename
- Contains full message history with all stage outputs

**CLAUDE.md**
- Project documentation for Claude Code sessions
- Contains architecture decisions and important notes
- Max ~500 tokens (kept minimal for context efficiency)

**.claude/memory/**
- Persistent context files for deep reference
- `architecture.md` - System design details
- `conventions.md` - Code patterns and style
- `glossary.md` - This file, key terms

**.claude/plans/**
- User-managed directory for session plans
- Not auto-generated

**.claude/checkpoints/**
- User-managed directory for progress tracking
- Not auto-generated

## Environment Terms

**localhost:8001**
- Backend API server port
- Frontend configured to call `http://localhost:8001`
- Changed from 8000 to avoid conflicts

**localhost:5173**
- Frontend Vite dev server default port
- Backend CORS allows this origin

**OPENROUTER_API_KEY**
- Environment variable containing API key
- Loaded via `python-dotenv` from `.env`
- Required for any model queries

## SEARCH KEYWORDS
`anonymization`, `council models`, `chairman`, `stage 1 2 3`, `graceful degradation`, `ranking aggregation`, `label mapping`, `openrouter`, `metadata`, `de-anonymization`
