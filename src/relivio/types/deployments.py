from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class RegisterDeploymentInput:
    version: Optional[str] = None
    note: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    idempotency_key: Optional[str] = None


@dataclass(frozen=True)
class RegisterDeploymentResponse:
    id: str
    version: Optional[str]
    summary_scheduled: bool
