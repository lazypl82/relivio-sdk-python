# Rationale

## Problem

Relivio adoption should not require each service to hand-build raw ingest payloads,
but the SDK must also avoid becoming a framework adapter or observability agent.

The repeated integration work is:

- register deployment
- send single ingest log
- send ingest batch
- convert exceptions into ingest logs
- read protection status for guard code without SDK-side verdict interpretation
- read latest verdict for guard decisions when needed

The SDK should remove that boilerplate without changing Relivio's product contract.

## Direction

Build a primitive Python SDK that maps language-level constructs to Relivio API calls.

The SDK is intentionally narrow:

- stateless HTTP wrapper
- only one narrow latest verdict read
- explicit exception capture helper
- no framework adapters
- no runtime guard logic
- no auto instrumentation

## Current Status

Primitive `0.1.0` surface is implemented:

- `deployments.register()`
- `ingest.send()`
- `ingest.send_batch()`
- `capture_exception()`
- `protection.get_status()`
- `verdicts.latest()`
- `status()`

Framework-specific wiring belongs in cookbook examples, not the SDK package.
