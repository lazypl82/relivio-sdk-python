from typing import Optional

from ..errors import RelivioApiError
from ..http import HttpTransport
from ..types.verdicts import LatestVerdictResponse


class VerdictsResource:
    def __init__(self, http: HttpTransport):
        self._http = http

    def latest(
        self,
        deployment_id: Optional[str] = None,
    ) -> Optional[LatestVerdictResponse]:
        return _request_latest(self._http, deployment_id)

    async def alatest(
        self,
        deployment_id: Optional[str] = None,
    ) -> Optional[LatestVerdictResponse]:
        return await _arequest_latest(self._http, deployment_id)


def _build_query(deployment_id: Optional[str]):
    if not deployment_id:
        return None
    return {"deployment_id": deployment_id}


def _map_latest_verdict(raw) -> LatestVerdictResponse:
    return LatestVerdictResponse(
        id=str(raw["id"]),
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
        action_detail=(
            raw.get("recommended_action_detail")
            if isinstance(raw.get("recommended_action_detail"), str)
            else None
        ),
        affected_apis=[
            item for item in raw.get("affected_apis", []) if isinstance(item, str)
        ],
        top_signals=[
            item for item in raw.get("top_signals", []) if isinstance(item, str)
        ],
        created_at=str(raw["created_at"]),
    )


def _request_latest(
    http: HttpTransport,
    deployment_id: Optional[str],
) -> Optional[LatestVerdictResponse]:
    try:
        raw = http.request(
            method="GET",
            path="/api/v1/summaries/latest",
            params=_build_query(deployment_id),
        )
    except RelivioApiError as exc:
        if exc.status == 404:
            return None
        raise
    return _map_latest_verdict(raw)


async def _arequest_latest(
    http: HttpTransport,
    deployment_id: Optional[str],
) -> Optional[LatestVerdictResponse]:
    try:
        raw = await http.arequest(
            method="GET",
            path="/api/v1/summaries/latest",
            params=_build_query(deployment_id),
        )
    except RelivioApiError as exc:
        if exc.status == 404:
            return None
        raise
    return _map_latest_verdict(raw)
