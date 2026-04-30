from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ErrorPayload:
    code: str
    message: str
    request_id: Optional[str] = None
