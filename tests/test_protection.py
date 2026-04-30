from relivio import ProtectionStatusInput, Relivio
import pytest


def test_protection_get_status_maps_query_and_response(respx_mock):
    route = respx_mock.get(
        "https://api.relivio.dev/api/v1/protection/status",
        params={
            "service": "api",
            "api_path": "/api/orders/123",
            "method": "POST",
        },
    ).respond(
        status_code=200,
        json={
            "deployment_id": "dep_1",
            "verdict": "WATCH",
            "decision_tier": "guard_ready",
            "recommended_action": "Keep guard ready",
            "recommended_action_detail": "inspect /api/orders",
            "protection_guidance": {
                "target": "/api/orders/:id",
                "guard_strategy": "fail-fast",
            },
            "affected_apis": ["/api/orders/:id"],
            "requested_service": "api",
            "requested_api_path": "/api/orders/:id",
            "requested_method": "POST",
            "matched_api_path": "/api/orders/:id",
            "created_at": "2026-04-30T01:00:00Z",
        },
    )

    client = Relivio(api_key="rk_test")
    status = client.protection.get_status(
        ProtectionStatusInput(
            service="api",
            api_path="/api/orders/123",
            method="POST",
        )
    )

    assert route.called
    assert status.deployment_id == "dep_1"
    assert status.verdict == "WATCH"
    assert status.decision_tier == "guard_ready"
    assert status.protection_guidance == {
        "target": "/api/orders/:id",
        "guard_strategy": "fail-fast",
    }
    assert status.affected_apis == ["/api/orders/:id"]
    assert status.requested_service == "api"
    assert status.requested_api_path == "/api/orders/:id"
    assert status.requested_method == "POST"
    assert status.matched_api_path == "/api/orders/:id"


@pytest.mark.asyncio
async def test_protection_aget_status_uses_async_transport(respx_mock):
    route = respx_mock.get("https://api.relivio.dev/api/v1/protection/status").respond(
        status_code=200,
        json={
            "deployment_id": "dep_2",
            "verdict": "STABLE",
            "decision_tier": "inform",
            "recommended_action": None,
            "recommended_action_detail": None,
            "protection_guidance": None,
            "affected_apis": [],
            "requested_service": None,
            "requested_api_path": None,
            "requested_method": None,
            "matched_api_path": None,
            "created_at": "2026-04-30T01:00:00Z",
        },
    )

    client = Relivio(api_key="rk_test")
    status = await client.protection.aget_status()

    assert route.called
    assert status.deployment_id == "dep_2"
    assert status.decision_tier == "inform"
