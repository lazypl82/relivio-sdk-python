import pytest

from relivio import Relivio


def test_capture_exception_maps_to_ingest_and_swallows_success(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/ingest/log").respond(
        status_code=202,
        json={"status": "accepted", "log_event_id": "log_1"},
    )
    client = Relivio(api_key="rk_test")

    try:
        raise TypeError("boom")
    except TypeError as exc:
        client.capture_exception(
            exc,
            service="checkout-api",
            api_path="/api/orders/123",
            trace_id="trace_1",
        )

    assert route.called
    body = route.calls.last.request.content.decode("utf-8")
    assert '"level":"ERROR"' in body
    assert '"message":"boom"' in body
    assert '"service":"checkout-api"' in body
    assert '"api_path":"/api/orders/123"' in body
    assert '"trace_id":"trace_1"' in body
    assert '"error_type":"TypeError"' in body
    assert "Traceback" in body
    assert client.status().captured_events == 1
    assert client.status().capture_send_failures == 0


def test_capture_exception_failures_stay_inside_sdk_status(respx_mock):
    respx_mock.post("https://api.relivio.dev/api/v1/ingest/log").respond(
        status_code=500,
        json={"error": {"code": "BOOM", "message": "server down"}},
    )
    client = Relivio(api_key="rk_test")

    try:
        raise RuntimeError("captured")
    except RuntimeError as exc:
        client.capture_exception(exc)

    status = client.status()
    assert status.captured_events == 1
    assert status.capture_send_failures == 1
    assert "server down" in (status.last_capture_error or "")


@pytest.mark.asyncio
async def test_acapture_exception_uses_async_ingest(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/ingest/log").respond(
        status_code=202,
        json={"status": "accepted", "log_event_id": "log_async"},
    )
    client = Relivio(api_key="rk_test")

    try:
        raise ValueError("async boom")
    except ValueError as exc:
        await client.acapture_exception(exc, service="worker")

    assert route.called
    body = route.calls.last.request.content.decode("utf-8")
    assert '"message":"async boom"' in body
    assert '"service":"worker"' in body
    assert client.status().captured_events == 1
