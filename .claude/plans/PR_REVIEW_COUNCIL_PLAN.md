# PR Review Council - Architecture & Implementation Plan

## Context

The LLM Council project (forked from karpathy/llm-council) is a 3-stage deliberation system where multiple LLMs answer questions, anonymously peer-review each other, and a chairman synthesizes a final answer. We're rebuilding this as a **PR Review Council** — same 3-stage pipeline concept, but purpose-built for code review with a key innovation: **debate-based peer review** instead of simple ranking.

The core insight: AI code reviewers today produce too many false positives. By having multiple specialized models **debate** each other's findings, we can filter noise and surface only high-confidence, actionable feedback.

**Build approach**: Fork and rebuild as its own focused project.

---

## Architecture Overview

### The 3-Stage Pipeline (adapted for code review)

```
PR Diff + Project Context
    |
Stage 1: Specialized Reviews (parallel)
    Security reviewer (Claude) + Performance reviewer (Grok) +
    Architecture reviewer (GPT) + Readability reviewer (Gemini)
    -> Structured findings with severity, file, line, suggestion
    |
Stage 2: DEBATE (adaptive rounds)
    Round 1: Each model reviews ALL findings, responds: confirm/challenge/dismiss
    -> If critical/high findings are disputed -> Round 2 (focused on disputes only)
    -> Max 3 rounds, hard cap
    -> Resolution: consensus / disputed / dismissed
    |
Stage 3: Chairman Synthesis (Gemini)
    -> Structured review: Must Fix | Should Fix | Consider | Praise
    -> Verdict: approve / request_changes / comment
    |
Output: Web UI / CLI markdown / GitHub PR comments
```

### Interfaces (all share the same core engine)

1. **Web UI** (React + Vite) — SSE streaming, progressive stage display
2. **CLI** (Click) — local review before pushing, markdown output
3. **GitHub Action** — auto-reviews PRs, posts comments directly

---

## Key Design Decisions

### Stage 1: Specialized Reviewer Roles

Each model gets a **role-specific system prompt** (unlike the original where all models get the same prompt). Each reviewer outputs structured `FINDING/END_FINDING` blocks:

```
FINDING:
- severity: critical|high|medium|low|info
- file: <path from diff>
- line: <line number or range>
- category: security|performance|architecture|readability
- title: <one-line summary>
- description: <detailed explanation>
- suggestion: <specific code fix>
END_FINDING
```

**Model-to-role mapping:**
| Role | Model | Rationale |
|------|-------|-----------|
| Security | `anthropic/claude-sonnet-4.5` | Strong reasoning about injection, auth bypass |
| Performance | `x-ai/grok-4` | Analytical capability for complexity analysis |
| Architecture | `openai/gpt-5.1` | Broad design pattern knowledge |
| Readability | `google/gemini-3-pro-preview` | Large context window, style consistency |
| **Chairman** | `google/gemini-3-pro-preview` | Best at synthesizing large contexts |

### Stage 2: Debate Format (replaces ranking)

**Round 1 prompt**: Each model sees ALL findings from ALL reviewers and responds to each:
```
RESPONSE_TO: {finding_id}
verdict: confirm|challenge|dismiss
confidence: high|medium|low
reasoning: <specific technical counter-evidence>
END_RESPONSE
```

**Adaptive escalation**: Another round triggers only if critical/high findings have both `confirm` AND `challenge/dismiss` verdicts. Round 2+ focuses exclusively on disputed findings.

**Resolution logic**: >60% confirm = consensus, >60% dismiss = dismissed, otherwise = disputed. Max 3 rounds.

### Stage 3: Structured Output

Chairman produces categorized review (not prose):
- **VERDICT**: approve | request_changes | comment
- **MUST_FIX**: Consensus critical/high findings
- **SHOULD_FIX**: Consensus medium + disputed high where chairman sides with challengers
- **CONSIDER**: Low severity, stylistic, disputed items worth thinking about
- **PRAISE**: What the PR does well

### Smart File Grouping (preprocessing)

Before Stage 1, files are grouped into logical review units:
- Test pairs: `component.tsx` + `component.test.tsx`
- Component bundles: same-name files across extensions
- API routes: handler + middleware + types
- Config groups: related config files together

For large PRs (>2000 lines), groups are reviewed in parallel batches with cross-reference summaries.

### Project Context Injection

Each reviewer receives project context loaded from the repo:
- `CLAUDE.md` / `AGENTS.md` (highest priority, up to 2000 tokens)
- Summarized ESLint/Prettier/TSConfig rules
- Package dependencies
- Detected language/framework

---

## Project Structure

```
pr-review-council/
  backend/
    __init__.py
    config.py              # Model roles, API keys, constants
    openrouter.py          # Async OpenRouter client (adapted — adds system prompt support)
    input.py               # Diff parsing: raw diff, git diff, GitHub API
    context.py             # Project context loading (CLAUDE.md, configs)
    file_grouping.py       # Smart file grouping logic
    review_council.py      # 3-stage pipeline orchestration
    debate.py              # Stage 2 debate + adaptive escalation
    parsers.py             # FINDING/RESPONSE/VERDICT block parsers
    output.py              # Formatters: GitHub review, markdown, JSON
    storage.py             # JSON file storage for review sessions
    models.py              # Pydantic data models
    main.py                # FastAPI app with SSE streaming
  cli/
    main.py                # Click CLI tool
  github_action/
    action.yml             # GitHub Action definition
    entrypoint.py          # Action entrypoint
  frontend/
    src/
      api.js               # API client with SSE stream support
      App.jsx              # Review session management
      components/
        Sidebar.jsx        # Review session list
        ReviewInterface.jsx # Main review area
        PRSummary.jsx      # PR metadata + diff stats
        Stage1Reviews.jsx  # Tabbed specialist reviews + findings table
        Stage2Debate.jsx   # Debate visualization (3 views: summary/by-finding/by-round)
        FindingDebateCard.jsx  # Per-finding debate thread
        ConsensusPanel.jsx # Resolution bar: confirmed/disputed/dismissed
        Stage3FinalReview.jsx  # Categorized final review
        VerdictBanner.jsx  # Approve/request changes banner
        DiffViewer.jsx     # Inline diff with finding annotations
  data/reviews/            # Review session JSON storage
```

### Data Model (key types)

- **ReviewSession**: Top-level object (replaces Conversation) — contains PR metadata, all 3 stages, status
- **Finding**: Structured issue with severity, file, line, category, title, description, suggestion, status
- **DebateRound**: One round of debate — contains responses per reviewer + new findings
- **FindingResponse**: A reviewer's verdict on a specific finding (confirm/challenge/dismiss + reasoning)
- **DebateResolution**: Final categorization — consensus/disputed/dismissed finding IDs
- **ReviewOutput**: Chairman's structured output — verdict, must_fix, should_fix, consider, praise

### SSE Events (streaming protocol)

```
stage1_start -> stage1_reviewer_complete (per reviewer) -> stage1_complete
stage2_start -> debate_round_start -> debate_response_complete (per debater) -> debate_round_complete
  -> [if escalating: another round] -> stage2_complete (with resolution)
stage3_start -> stage3_complete (with structured review)
complete
```

---

## Reuse from Original Project

These patterns from the existing codebase will be adapted:
- `backend/openrouter.py` — async HTTP client (add system prompt parameter)
- `backend/main.py` lines 126-194 — SSE streaming pattern with `StreamingResponse`
- `frontend/src/App.jsx` lines 93-172 — SSE event handling + progressive state updates
- `frontend/src/components/Stage2.jsx` — tab component pattern, CSS structure
- `backend/storage.py` — JSON file storage pattern (adapt for ReviewSession instead of Conversation)

---

## Implementation Phases

### Phase 1: Core Engine (MVP) — get reviews working via CLI
1. `backend/models.py` — Pydantic data models
2. `backend/config.py` — model/role configuration
3. `backend/openrouter.py` — adapt from original (add system prompt)
4. `backend/input.py` — unified diff parser + `git diff` support
5. `backend/parsers.py` — FINDING block parser
6. `backend/review_council.py` — Stage 1 (parallel specialist reviews)
7. `backend/debate.py` — Stage 2 (debate with adaptive rounds)
8. Complete `review_council.py` — Stage 3 (chairman synthesis)
9. `backend/output.py` — markdown formatter
10. `cli/main.py` — basic CLI: `review-council review --base main`

### Phase 2: Web UI — visual debate exploration
11. `backend/main.py` — FastAPI + SSE streaming
12. `backend/storage.py` — review session persistence
13. Frontend components (Stage1Reviews, Stage2Debate, Stage3FinalReview)
14. FindingDebateCard + ConsensusPanel (debate visualization)

### Phase 3: GitHub Integration
15. `backend/input.py` — GitHub PR API integration
16. `backend/output.py` — GitHub review comment format
17. `github_action/` — action definition + webhook handler
18. Post-to-GitHub endpoint

### Phase 4: Polish
19. `backend/context.py` — project context injection
20. `backend/file_grouping.py` — smart file grouping
21. `DiffViewer.jsx` — inline diff with finding annotations

---

## Verification Plan

### Phase 1 Testing
- Create a sample diff file, run through CLI, verify structured findings output
- Test with a real `git diff` on a local repo
- Verify debate rounds trigger correctly (create a diff with an intentional security issue to force disagreement)
- Verify adaptive escalation: simple PR = 1 round, controversial PR = 2-3 rounds

### Phase 2 Testing
- Start backend (`python -m backend.main`), start frontend (`npm run dev`)
- Submit a diff via web UI, verify SSE progressive updates render each stage
- Verify debate visualization shows confirm/challenge/dismiss per finding
- Verify consensus panel shows correct proportions

### Phase 3 Testing
- Review a real GitHub PR by URL
- Verify findings are posted as inline PR comments at correct file/line
- Test GitHub Action with a test repository
