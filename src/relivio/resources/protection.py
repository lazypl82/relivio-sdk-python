from typing import Dict, Optional

from ..http import HttpTransport
from ..types.protection import ProtectionStatusInput, ProtectionStatusResponse


class ProtectionResource:
    def __init__(self, http: HttpTransport):
        self._http = http

    def get_status(
        self,
        input: Optional[ProtectionStatusInput] = None,
    ) -> ProtectionStatusResponse:
        raw = self._http.request(
            method="GET",
            path="/api/v1/protection/status",
            params=_build_query(input),
        )
        return _map_status(raw)

    async def aget_status(
        self,
        input: Optional[ProtectionStatusInput] = None,
    ) -> ProtectionStatusResponse:
        raw = await self._http.arequest(
            method="GET",
            path="/api/v1/protection/status",
            params=_build_query(input),
        )
        return _map_status(raw)


def _build_query(input: Optional[ProtectionStatusInput]) -> Optional[Dict[str, str]]:
    if input is None:
        return None
    query: Dict[str, str] = {}
    if input.service:
        query["service"] = input.service
    if input.api_path:
        query["api_path"] = input.api_path
    if input.method:
        query["method"] = input.method
    if input.deployment_id:
        query["deployment_id"] = input.deployment_id
    return query or None


def _map_status(raw) -> ProtectionStatusResponse:
    guidance = raw.get("protection_guidance")
    if not isinstance(guidance, dict):
        guidance = None
    return ProtectionStatusResponse(
        deployment_id=str(raw["deployment_id"]),
        verdict=raw.get("verdict") if isinstance(raw.get("verdict"), str) else None,
        decision_tier=(
            raw.get("decision_tier")
            if isinstance(raw.get("decision_tier"), str)
            else None
        ),
        recommended_action=(
            raw.get("recommended_action")
            if isinstance(raw.get("recommended_action"), str)
            else None
        ),
        recommended_action_detail=(
            raw.get("recommended_action_detail")
            if isinstance(raw.get("recommended_action_detail"), str)
            else None
        ),
        protection_guidance=guidance,
        affected_apis=[
            item for item in raw.get("affected_apis", []) if isinstance(item, str)
        ],
        requested_service=(
            raw.get("requested_service")
            if isinstance(raw.get("requested_service"), str)
            else None
        ),
        requested_api_path=(
            raw.get("requested_api_path")
            if isinstance(raw.get("requested_api_path"), str)
            else None
        ),
        requested_method=(
            raw.get("requested_method")
            if isinstance(raw.get("requested_method"), str)
            else None
        ),
        matched_api_path=(
            raw.get("matched_api_path")
            if isinstance(raw.get("matched_api_path"), str)
            else None
        ),
        created_at=str(raw["created_at"]),
    )
