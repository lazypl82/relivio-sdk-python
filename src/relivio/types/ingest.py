from dataclasses import dataclass
from typing import List, Literal, Optional

LogLevel = Literal["ERROR", "WARN"]


@dataclass
class IngestLogInput:
    level: LogLevel
    message: str
    stacktrace: Optional[str] = None
    service: Optional[str] = None
    api_path: Optional[str] = None
    trace_id: Optional[str] = None
    error_type: Optional[str] = None
    idempotency_key: Optional[str] = None


@dataclass(frozen=True)
class IngestLogResponse:
    status: str
    log_event_id: str


@dataclass
class IngestBatchInput:
    logs: List[IngestLogInput]
    idempotency_key: Optional[str] = None


@dataclass(frozen=True)
class IngestBatchResponse:
    status: str
    accepted_count: int
    log_event_ids: List[str]
