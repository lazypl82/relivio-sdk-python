# relivio

Primitive Python client for Relivio deploy registration, ingest, and exception capture.

[PyPI](https://pypi.org/project/relivio/) · [GitHub](https://github.com/lazypl82/relivio-sdk-python)

## Status

- current package scope: `0.1.0`
- supported Python versions: `3.9+`
- current public surface:
  - `deployments.register()`
  - `deployments.register_from_environment()`
  - `ingest.send()`
  - `ingest.asend()`
  - `ingest.send_batch()`
  - `capture_exception()`
  - `acapture_exception()`
  - `protection.get_status()`
  - `verdicts.latest()`
  - `status()`
- automatic retry only for `429 RATE_LIMITED`

## Non-goals

- full verdict consumer surface
- feedback/history/list/search APIs
- guard or middleware implementation
- broad auto instrumentation or metric collection
- framework adapters
- request object parsing

## Installation

```bash
pip install relivio
```

Verify the installed package:

```bash
python -c "import relivio; print(relivio.__all__)"
```

For local development:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from relivio import Relivio, IngestLogInput

relivio = Relivio(api_key="rk_...")

deployment = relivio.deployments.register()
print(deployment.id)

result = relivio.ingest.send(
    IngestLogInput(
        level="ERROR",
        message="checkout failed",
        api_path="/api/orders/finalize",
    )
)
print(result.log_event_id)

verdict = relivio.verdicts.latest()
if verdict is not None:
    print(verdict.verdict, verdict.decision_tier)
```

Capture exceptions explicitly from the boundary that already knows the safe path/context:

```python
try:
    run_usecase()
except Exception as exc:
    relivio.capture_exception(
        exc,
        service="checkout-api",
        api_path="/api/orders/{id}",
        trace_id="req_123",
    )
    raise
```

Read protection status explicitly from guard code:

```python
from relivio import ProtectionStatusInput

status = relivio.protection.get_status(
    ProtectionStatusInput(
        service="checkout-api",
        api_path="/api/orders/{id}",
        method="POST",
    )
)

print(status.decision_tier, status.matched_api_path)
```

## Async Example

```python
import asyncio
from relivio import Relivio, RegisterDeploymentInput

relivio = Relivio(api_key="rk_...")

async def main() -> None:
    deployment = await relivio.deployments.aregister(
        RegisterDeploymentInput(version="1.2.3")
    )
    print(deployment.id)

    try:
        await run_usecase()
    except Exception as exc:
        await relivio.acapture_exception(
            exc,
            service="checkout-api",
            api_path="/api/orders/{id}",
        )
        raise

asyncio.run(main())
```

## Development

```bash
python -m venv .venv
./.venv/bin/pip install -e ".[dev]"
./.venv/bin/pytest
./.venv/bin/python -m build
```

## Behavior Notes

- API key is sent through `X-API-Key`
- `Idempotency-Key` is supported for v0 writer endpoints
- 429 responses are retried with `Retry-After`
- 5xx responses are not retried
- server can accept gzip payloads, but SDK v0 sends plain JSON only
- SDK code never receives framework request objects
- `capture_exception()` is an ingest helper, not a framework adapter
- `capture_exception()` swallows Relivio delivery failures and records them in local `status()`
- `protection.get_status()` is a thin read over `/api/v1/protection/status`; it does not make block/allow decisions
- `verdicts.latest()` is intentionally narrow and only exists to support service-side guard logic
- `verdicts.latest()` returns `None` on 404 when a verdict is not available yet
- `status()` reports SDK self-diagnostics locally; it does not send host metrics to Relivio

## Related Repos

- [`relivio-server`](https://github.com/lazypl82/relivio-api): server-side deploy registration, ingest, and summary generation
- [`relivio-mcp`](https://github.com/lazypl82/relivio-mcp): agent-facing verdict consumer surface

## Security

Do not commit project API keys. Keep `X-API-Key` values in environment variables or local secret storage outside source control.

## Contributing

Small, behavior-preserving changes are preferred. Keep transport, resource, type, and error responsibilities separate, and run the smallest effective test/build checks before sending a change.
