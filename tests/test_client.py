from relivio import Relivio


def test_client_exposes_resources():
    client = Relivio(api_key="rk_test")
    assert client.deployments is not None
    assert client.ingest is not None
    assert client.verdicts is not None
    assert client.capture is not None
    assert client.status().captured_events == 0
    assert client.status().capture_send_failures == 0
    assert client.status().last_capture_error is None
    assert client.stats() == client.status()
