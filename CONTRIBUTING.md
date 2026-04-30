# Contributing

## Scope

This repository is intentionally narrow.

Current scope:
- deploy registration
- single log ingest
- batch log ingest
- explicit exception capture helper
- protection status read for guard code
- one minimal latest verdict read for service-side guard flows
- local SDK status

Do not expand the SDK into:
- a full verdict consumer surface
- broad framework middleware
- framework adapters
- request object parsing
- auto instrumentation
- runtime guard logic

## Development

```bash
python -m venv .venv
./.venv/bin/pip install -e ".[dev]"
./.venv/bin/pytest
./.venv/bin/python -m build
```

## Design Rules

- Keep the SDK as a thin HTTP wrapper over existing Relivio server contracts.
- Keep framework-specific wiring in cookbook examples, not package runtime code.
- Preserve snake_case wire format at the transport boundary and keep public Python types explicit.
- Keep human-facing explanation surfaces out of this SDK unless the contract explicitly requires them.
- Prefer small additive changes over broad abstractions.

## Pull Request Expectations

- One logical change per commit.
- Update tests and docs together when behavior or package scope changes.
- Call out any server-contract assumption explicitly.
