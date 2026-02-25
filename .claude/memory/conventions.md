# Code Conventions & Patterns

## Backend Conventions

### Python Style
- **Imports**: Use relative imports (`from .module import ...`)
- **Type hints**: Pydantic `BaseModel` for API request/response schemas
- **Async pattern**: `async/await` throughout for concurrent operations
- **Error handling**: Return None on failure, let caller decide handling
- **Documentation**: Docstrings on all public functions with Args/Returns

### FastAPI Patterns
- Request models inherit from `BaseModel` with type annotations
- Response models also use `BaseModel`
- CORS configured at app initialization
- All async handlers return structured responses

### Council Logic Patterns
```python
# Stage functions return typed data structures:
stage1_results: List[Dict[str, Any]]  # [{model, response}, ...]
rankings: Tuple[List[...], Dict[str, str]]  # (rankings_list, label_to_model)

# Anonymization creates mapping:
label_to_model = {"Response A": "openai/gpt-5.1", ...}
```

### Error Handling Pattern
```python
# Collect all responses, skip failures
responses = await query_models_parallel(models, messages)
for model, response in responses.items():
    if response is not None:
        results.append(...)
```

## Frontend Conventions

### React Component Structure
- Functional components with hooks
- Props used for data flow
- State managed in `App.jsx` for conversations
- Each stage (1, 2, 3) has dedicated component

### Component Patterns
```jsx
// Stage component structure:
export function StageName({ responses, metadata }) {
  return (
    <div className="stage-container">
      <TabbedInterface items={responses} />
    </div>
  )
}
```

### API Client Pattern
- Single `api.js` module with exported `api` object
- Each method handles fetch + error checking + JSON parsing
- Streaming handled via EventSource-style chunked reading
- No retries at client level

### Markdown Rendering
```jsx
// ALL markdown must be wrapped:
<div className="markdown-content">
  <ReactMarkdown>{content}</ReactMarkdown>
</div>
```

### Styling Conventions
- Global styles in `index.css`
- Component-specific CSS in `.css` files (co-located)
- Primary color: `#4a90e2` (blue)
- Light mode only (no dark mode)
- `.markdown-content` class: 12px padding all sides

## Configuration

### Backend Configuration
- `config.py` hardcodes model lists
- Models are OpenRouter identifiers (e.g., "openai/gpt-5.1")
- Environment: `OPENROUTER_API_KEY` in `.env`
- Port: 8001 (backend), 5173 (frontend) - hardcoded in both files

### Frontend Configuration
- `API_BASE = 'http://localhost:8001'` in `api.js`
- No environment variables used (hardcoded localhost)

## Storage Conventions

### JSON File Structure
```
data/conversations/
├── {uuid1}.json
├── {uuid2}.json
└── ...

Each file:
{
  "id": "uuid",
  "created_at": "ISO8601",
  "messages": [
    {"role": "user", "content": "..."},
    {
      "role": "assistant",
      "stage1": [{model, response}, ...],
      "stage2": [{model, evaluations, parsed_ranking}, ...],
      "stage3": "final answer"
    }
  ]
}
```

## Testing Approach
- Use `test_openrouter.py` to verify API connectivity
- Test before adding new model identifiers to council
- Both streaming and non-streaming modes supported

## SEARCH KEYWORDS
`relative imports`, `async/await`, `BaseModel`, `type hints`, `graceful degradation`, `react hooks`, `markdown-content`, `json storage`, `openrouter models`, `fastapi cors`
