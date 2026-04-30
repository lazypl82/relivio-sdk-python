from relivio import IngestBatchInput, IngestLogInput, Relivio


def test_send_ingest_log_maps_wire_fields(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/ingest/log").respond(
        status_code=202,
        json={"status": "accepted", "log_event_id": "log_1"},
    )

    client = Relivio(api_key="rk_test")
    result = client.ingest.send(
        IngestLogInput(
            level="ERROR",
            message="boom",
            api_path="/api/orders/finalize",
            trace_id="trace_1",
            error_type="DatabaseConnectionError",
        )
    )

    request = route.calls.last.request
    assert request.headers["X-API-Key"] == "rk_test"
    assert request.content
    assert result.status == "accepted"
    assert result.log_event_id == "log_1"


def test_send_ingest_batch_success(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/ingest/logs").respond(
        status_code=202,
        json={
            "status": "accepted",
            "accepted_count": 2,
            "log_event_ids": ["log_1", "log_2"],
        },
    )

    client = Relivio(api_key="rk_test")
    result = client.ingest.send_batch(
        IngestBatchInput(
            logs=[
                IngestLogInput(level="ERROR", message="one"),
                IngestLogInput(level="WARN", message="two"),
            ],
            idempotency_key="batch-1",
        )
    )

    request = route.calls.last.request
    assert request.headers["Idempotency-Key"] == "batch-1"
    assert result.accepted_count == 2
    assert result.log_event_ids == ["log_1", "log_2"]
