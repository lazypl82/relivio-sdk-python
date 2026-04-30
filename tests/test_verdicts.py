from relivio import Relivio


def test_verdicts_latest_returns_minimal_guard_surface(respx_mock):
    route = respx_mock.get("https://api.relivio.dev/api/v1/summaries/latest").respond(
        status_code=200,
        json={
            "id": "sum_1",
            "deployment_id": "dep_1",
            "verdict": "WATCH",
            "decision_tier": "guard_ready",
            "recommended_action": "Keep guard ready",
            "recommended_action_detail": "inspect /api/orders/finalize",
            "affected_apis": ["/api/orders/finalize"],
            "top_signals": ["service concentration HHI=0.50"],
            "created_at": "2026-04-21T12:00:00Z",
        },
    )

    client = Relivio(api_key="rk_test")
    result = client.verdicts.latest()

    assert route.called
    assert result.deployment_id == "dep_1"
    assert result.verdict == "WATCH"
    assert result.decision_tier == "guard_ready"
    assert result.affected_apis == ["/api/orders/finalize"]
    assert result.action_detail == "inspect /api/orders/finalize"
    assert result.top_signals == ["service concentration HHI=0.50"]


def test_verdicts_latest_passes_deployment_id_query(respx_mock):
    route = respx_mock.get(
        "https://api.relivio.dev/api/v1/summaries/latest",
        params={"deployment_id": "dep_2"},
    ).respond(
        status_code=200,
        json={
            "id": "sum_2",
            "deployment_id": "dep_2",
            "verdict": "RISK",
            "decision_tier": "block_recommended",
            "recommended_action": "Pause rollout",
            "recommended_action_detail": "inspect /api/orders/finalize first",
            "affected_apis": ["/api/orders/finalize"],
            "top_signals": ["dominant route concentration"],
            "created_at": "2026-04-21T12:05:00Z",
        },
    )

    client = Relivio(api_key="rk_test")
    result = client.verdicts.latest("dep_2")

    assert route.called
    assert result.deployment_id == "dep_2"
    assert result.verdict == "RISK"
    assert result.top_signals == ["dominant route concentration"]


def test_verdicts_latest_returns_none_on_not_found(respx_mock):
    route = respx_mock.get("https://api.relivio.dev/api/v1/summaries/latest").respond(
        status_code=404,
        json={
            "error": {
                "code": "SUMMARY_NOT_FOUND",
                "message": "Summary not available yet",
                "request_id": "req_404",
            }
        },
    )

    client = Relivio(api_key="rk_test")
    result = client.verdicts.latest()

    assert route.called
    assert result is None
