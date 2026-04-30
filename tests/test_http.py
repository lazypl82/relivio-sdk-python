import pytest

from relivio import Relivio
from relivio.errors import RelivioApiError


def test_http_retries_rate_limit_until_success(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/deployments")
    route.side_effect = [
        ResponseSpec(
            status_code=429,
            json_body={
                "error": {
                    "code": "RATE_LIMITED",
                    "message": "slow down",
                    "request_id": "req_1",
                }
            },
            headers={"Retry-After": "0"},
        ),
        ResponseSpec(
            status_code=201,
            json_body={
                "id": "dep_3",
                "version": "1.0.0",
                "summary_scheduled": True,
            },
        ),
    ]

    client = Relivio(api_key="rk_test")
    result = client.deployments.register()

    assert result.id == "dep_3"
    assert len(route.calls) == 2


def test_http_raises_after_retry_budget_exhausted(respx_mock):
    route = respx_mock.post("https://api.relivio.dev/api/v1/deployments")
    route.side_effect = [
        ResponseSpec(
            status_code=429,
            json_body={
                "error": {
                    "code": "RATE_LIMITED",
                    "message": "retry later",
                    "request_id": "req_2",
                }
            },
            headers={"Retry-After": "0"},
        )
        for _ in range(4)
    ]

    client = Relivio(api_key="rk_test")
    with pytest.raises(RelivioApiError) as exc_info:
        client.deployments.register()

    assert exc_info.value.status == 429
    assert exc_info.value.code == "RATE_LIMITED"
    assert len(route.calls) == 4


class ResponseSpec:
    def __init__(self, status_code: int, json_body: dict, headers=None):
        self.status_code = status_code
        self.json_body = json_body
        self.headers = headers or {}

    def __call__(self, request):
        import httpx

        return httpx.Response(
            status_code=self.status_code,
            json=self.json_body,
            headers=self.headers,
            request=request,
        )
