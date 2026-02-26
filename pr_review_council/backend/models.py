"""Pydantic models for PR Review Council."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, model_validator


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
    CONSENSUS = "consensus"  # >60% confirm
    DISMISSED = "dismissed"  # >60% dismiss
    DISPUTED = "disputed"  # neither threshold met


class ReviewVerdict(str, Enum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    COMMENT = "comment"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FindingStatus(str, Enum):
    OPEN = "open"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"


class ReviewSessionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Finding(BaseModel):
    """A single code review finding from a specialist reviewer."""

    id: str  # e.g. "F1", "F2"
    reviewer: str  # role name, e.g. "security"
    severity: Severity
    category: Category
    file: str
    line_start: int = None
    line_end: int = None
    title: str
    description: str
    suggestion: str = None
    raw_text: str = None  # original block for debugging
    status: FindingStatus = FindingStatus.OPEN


class FindingResponse(BaseModel):
    """A reviewer's response to a finding during Stage 2 debate."""

    finding_id: str  # references Finding.id
    reviewer: str  # who is responding
    verdict: DebateVerdict
    reasoning: str
    confidence: Confidence = Confidence.MEDIUM
    raw_text: str = None


class DebateRound(BaseModel):
    """One round of the Stage 2 debate."""

    round_num: int
    responses: list[FindingResponse]
    findings_in_scope: list[str]  # finding IDs debated this round


class DebateResolution(BaseModel):
    """Resolution for a single finding after all debate rounds."""

    finding_id: str
    consensus: ConsensusResult
    confirm_count: int
    challenge_count: int
    dismiss_count: int
    total_responses: int

    @model_validator(mode="after")
    def check_counts_sum(self) -> "DebateResolution":
        if (
            self.confirm_count + self.challenge_count + self.dismiss_count
            != self.total_responses
        ):
            raise ValueError(
                "confirm_count + challenge_count + dismiss_count must equal total_responses"
            )
        return self


class ReviewItem(BaseModel):
    """A single actionable item in the final review output."""

    finding_id: str
    severity: Severity
    category: Category
    file: str
    line_start: int = None
    line_end: int = None
    title: str
    description: str
    suggestion: str = None


class ReviewOutput(BaseModel):
    """Stage 3: Chairman's synthesized final review."""

    verdict: ReviewVerdict
    summary: str
    must_fix: list[ReviewItem] = Field(default_factory=list)
    should_fix: list[ReviewItem] = Field(default_factory=list)
    consider: list[ReviewItem] = Field(default_factory=list)
    praise: list[str] = Field(default_factory=list)
    raw_text: str = None


class ReviewSession(BaseModel):
    """A complete PR review session (persisted to storage)."""

    id: str
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    status: ReviewSessionStatus = ReviewSessionStatus.PENDING
    pr_title: str = None
    pr_url: str = None
    diff_summary: str = None  # brief description for listing

    # Stage results
    stage1_findings: list[Finding] = Field(default_factory=list)
    stage2_rounds: list[DebateRound] = Field(default_factory=list)
    stage2_resolutions: list[DebateResolution] = Field(default_factory=list)
    stage3_output: ReviewOutput = None

    # Runtime metadata (ephemeral - excluded from serialization)
    metadata: dict[str, Any] = Field(default_factory=dict, exclude=True)
