"""Pydantic models for PR Review Council."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Category(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    READABILITY = "readability"
    BUG = "bug"
    OTHER = "other"


class DebateVerdict(str, Enum):
    CONFIRM = "confirm"
    CHALLENGE = "challenge"
    DISMISS = "dismiss"


class ConsensusResult(str, Enum):
    CONSENSUS = "consensus"       # >60% confirm
    DISMISSED = "dismissed"       # >60% dismiss
    DISPUTED = "disputed"         # neither threshold met


class ReviewVerdict(str, Enum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    COMMENT = "comment"


class Finding(BaseModel):
    """A single code review finding from a specialist reviewer."""
    id: str                        # e.g. "F1", "F2"
    reviewer: str                  # role name, e.g. "security"
    severity: Severity
    category: Category
    file: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    title: str
    description: str
    suggestion: Optional[str] = None
    raw_text: Optional[str] = None  # original block for debugging


class FindingResponse(BaseModel):
    """A reviewer's response to a finding during Stage 2 debate."""
    finding_id: str               # references Finding.id
    reviewer: str                 # who is responding
    verdict: DebateVerdict
    reasoning: str
    raw_text: Optional[str] = None


class DebateRound(BaseModel):
    """One round of the Stage 2 debate."""
    round_num: int
    responses: List[FindingResponse]
    findings_in_scope: List[str]  # finding IDs debated this round


class DebateResolution(BaseModel):
    """Resolution for a single finding after all debate rounds."""
    finding_id: str
    consensus: ConsensusResult
    confirm_count: int
    challenge_count: int
    dismiss_count: int
    total_responses: int


class ReviewItem(BaseModel):
    """A single actionable item in the final review output."""
    finding_id: str
    severity: Severity
    file: str
    line_start: Optional[int] = None
    title: str
    description: str
    suggestion: Optional[str] = None


class ReviewOutput(BaseModel):
    """Stage 3: Chairman's synthesized final review."""
    verdict: ReviewVerdict
    summary: str
    must_fix: List[ReviewItem] = Field(default_factory=list)
    should_fix: List[ReviewItem] = Field(default_factory=list)
    consider: List[ReviewItem] = Field(default_factory=list)
    praise: List[str] = Field(default_factory=list)
    raw_text: Optional[str] = None


class ReviewSession(BaseModel):
    """A complete PR review session (persisted to storage)."""
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    pr_title: Optional[str] = None
    pr_url: Optional[str] = None
    diff_summary: Optional[str] = None   # brief description for listing

    # Stage results
    stage1_findings: List[Finding] = Field(default_factory=list)
    stage2_rounds: List[DebateRound] = Field(default_factory=list)
    stage2_resolutions: List[DebateResolution] = Field(default_factory=list)
    stage3_output: Optional[ReviewOutput] = None

    # Runtime metadata (ephemeral but included for completeness)
    metadata: Dict[str, Any] = Field(default_factory=dict)
