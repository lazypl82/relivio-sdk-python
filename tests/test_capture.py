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


def test_capture_uses_default_service_when_caller_omits(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/ingest/log").respond(
        status_code=202,
        json={"status": "accepted", "log_event_id": "log_default"},
    )
    client = Relivio(api_key="rk_test", default_service="checkout-api")

    try:
        raise TypeError("default boom")
    except TypeError as exc:
        client.capture_exception(exc, api_path="/api/orders")

    body = route.calls.last.request.content.decode("utf-8")
    assert '"service":"checkout-api"' in body


def test_capture_explicit_service_overrides_default(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/ingest/log").respond(
        status_code=202,
        json={"status": "accepted", "log_event_id": "log_override"},
    )
    client = Relivio(api_key="rk_test", default_service="checkout-api")

    try:
        raise TypeError("override boom")
    except TypeError as exc:
        client.capture_exception(exc, service="orders-worker")

    body = route.calls.last.request.content.decode("utf-8")
    assert '"service":"orders-worker"' in body


def test_capture_uses_trace_id_provider(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/ingest/log").respond(
        status_code=202,
        json={"status": "accepted", "log_event_id": "log_trace"},
    )
    client = Relivio(
        api_key="rk_test",
        trace_id_provider=lambda: "trace_from_provider",
    )

    try:
        raise TypeError("trace boom")
    except TypeError as exc:
        client.capture_exception(exc)

    body = route.calls.last.request.content.decode("utf-8")
    assert '"trace_id":"trace_from_provider"' in body


def test_capture_explicit_trace_id_overrides_provider(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/ingest/log").respond(
        status_code=202,
        json={"status": "accepted", "log_event_id": "log_trace_override"},
    )
    client = Relivio(
        api_key="rk_test",
        trace_id_provider=lambda: "from_provider",
    )

    try:
        raise TypeError("trace boom")
    except TypeError as exc:
        client.capture_exception(exc, trace_id="explicit_trace")

    body = route.calls.last.request.content.decode("utf-8")
    assert '"trace_id":"explicit_trace"' in body


def test_trace_id_provider_swallows_exception_and_falls_back_to_none(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/ingest/log").respond(
        status_code=202,
        json={"status": "accepted", "log_event_id": "log_trace_fallback"},
    )

    def broken_provider():
        raise RuntimeError("provider broken")

    client = Relivio(api_key="rk_test", trace_id_provider=broken_provider)

    try:
        raise TypeError("trace boom")
    except TypeError as exc:
        client.capture_exception(exc)

    body = route.calls.last.request.content.decode("utf-8")
    assert '"trace_id":null' in body
    assert client.status().captured_events == 1


def test_ingest_send_payload_is_not_mutated_by_default_service(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/ingest/log").respond(
        status_code=202,
        json={"status": "accepted", "log_event_id": "log_ingest_passthrough"},
    )
    client = Relivio(api_key="rk_test", default_service="checkout-api")

    from relivio.types.ingest import IngestLogInput

    client.ingest.send(
        IngestLogInput(
            level="ERROR",
            message="explicit ingest message",
        )
    )

    body = route.calls.last.request.content.decode("utf-8")
    assert '"service":null' in body
