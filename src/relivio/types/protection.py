from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ProtectionStatusInput:
    service: Optional[str] = None
    api_path: Optional[str] = None
    method: Optional[str] = None
    deployment_id: Optional[str] = None


@dataclass(frozen=True)
class ProtectionStatusResponse:
    deployment_id: str
    verdict: Optional[str]
    decision_tier: Optional[str]
    recommended_action: Optional[str]
    recommended_action_detail: Optional[str]
    protection_guidance: Optional[Dict[str, object]]
    affected_apis: List[str]
    requested_service: Optional[str]
    requested_api_path: Optional[str]
    requested_method: Optional[str]
    matched_api_path: Optional[str]
    created_at: str
