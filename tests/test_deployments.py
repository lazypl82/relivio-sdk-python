from relivio import RegisterDeploymentInput, Relivio


def test_register_deployment_success(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/deployments").respond(
        status_code=201,
        json={
            "id": "dep_1",
            "version": "1.2.3",
            "summary_scheduled": True,
        },
    )

    client = Relivio(api_key="rk_test")
    result = client.deployments.register(RegisterDeploymentInput(version="1.2.3"))

    assert route.called
    request = route.calls.last.request
    assert request.headers["X-API-Key"] == "rk_test"
    assert result.id == "dep_1"
    assert result.version == "1.2.3"
    assert result.summary_scheduled is True


def test_register_deployment_sets_idempotency_key(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/deployments").respond(
        status_code=201,
        json={
            "id": "dep_2",
            "version": None,
            "summary_scheduled": True,
        },
    )

    client = Relivio(api_key="rk_test")
    client.deployments.register(
        RegisterDeploymentInput(idempotency_key="idem-1", note="deploy")
    )

    request = route.calls.last.request
    assert request.headers["Idempotency-Key"] == "idem-1"


def test_register_from_environment_merges_runtime_metadata(respx_mock, monkeypatch):
    monkeypatch.setenv("RELIVIO_COMMIT_SHA", "abc123")
    route = respx_mock.post("https://api.relivio.dev/api/v1/deployments").respond(
        status_code=201,
        json={
            "id": "dep_env",
            "version": "abc123",
            "summary_scheduled": True,
        },
    )

    client = Relivio(api_key="rk_test")
    result = client.deployments.register_from_environment(
        RegisterDeploymentInput(metadata={"explicit": "kept"})
    )

    body = route.calls.last.request.content.decode("utf-8")
    assert '"version":"abc123"' in body
    assert '"commit_sha":"abc123"' in body
    assert '"runtime":"python"' in body
    assert '"explicit":"kept"' in body
    assert result.id == "dep_env"
