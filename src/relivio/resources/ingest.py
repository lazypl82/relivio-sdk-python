from typing import Dict

from ..http import HttpTransport
from ..types.ingest import (
    IngestBatchInput,
    IngestBatchResponse,
    IngestLogInput,
    IngestLogResponse,
)


class IngestResource:
    def __init__(self, http: HttpTransport):
        self._http = http

    def send(self, input: IngestLogInput) -> IngestLogResponse:
        raw = self._http.request(
            method="POST",
            path="/api/v1/ingest/log",
            body=_build_log_wire_body(input),
            idempotency_key=input.idempotency_key,
        )
        return IngestLogResponse(
            status=str(raw["status"]),
            log_event_id=str(raw["log_event_id"]),
        )

    async def asend(self, input: IngestLogInput) -> IngestLogResponse:
        raw = await self._http.arequest(
            method="POST",
            path="/api/v1/ingest/log",
            body=_build_log_wire_body(input),
            idempotency_key=input.idempotency_key,
        )
        return IngestLogResponse(
            status=str(raw["status"]),
            log_event_id=str(raw["log_event_id"]),
        )

    def send_batch(self, input: IngestBatchInput) -> IngestBatchResponse:
        raw = self._http.request(
            method="POST",
            path="/api/v1/ingest/logs",
            body={"logs": [_build_log_wire_body(log) for log in input.logs]},
            idempotency_key=input.idempotency_key,
        )
        return IngestBatchResponse(
            status=str(raw["status"]),
            accepted_count=int(raw["accepted_count"]),
            log_event_ids=[
                entry for entry in raw.get("log_event_ids", []) if isinstance(entry, str)
            ],
        )

    async def asend_batch(self, input: IngestBatchInput) -> IngestBatchResponse:
        raw = await self._http.arequest(
            method="POST",
            path="/api/v1/ingest/logs",
            body={"logs": [_build_log_wire_body(log) for log in input.logs]},
            idempotency_key=input.idempotency_key,
        )
        return IngestBatchResponse(
            status=str(raw["status"]),
            accepted_count=int(raw["accepted_count"]),
            log_event_ids=[
                entry for entry in raw.get("log_event_ids", []) if isinstance(entry, str)
            ],
        )


def _build_log_wire_body(input: IngestLogInput) -> Dict[str, object]:
    return {
        "level": input.level,
        "message": input.message,
        "stacktrace": input.stacktrace,
        "service": input.service,
        "api_path": input.api_path,
        "trace_id": input.trace_id,
        "error_type": input.error_type,
    }
