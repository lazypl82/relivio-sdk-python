from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class LatestVerdictResponse:
    id: str
    deployment_id: str
    verdict: Optional[str]
    decision_tier: Optional[str]
    recommended_action: Optional[str]
    action_detail: Optional[str]
    affected_apis: List[str]
    top_signals: List[str]
    created_at: str
