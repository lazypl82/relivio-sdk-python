import traceback
from dataclasses import dataclass
from typing import Optional

from .resources.ingest import IngestResource
from .stats import RelivioStatsStore
from .types.ingest import IngestLogInput, LogLevel
from .types.options import TraceIdProvider


@dataclass(frozen=True)
class CaptureExceptionInput:
    exception: BaseException
    service: Optional[str] = None
    level: LogLevel = "ERROR"
    api_path: Optional[str] = None
    trace_id: Optional[str] = None


class CaptureResource:
    def __init__(
        self,
        ingest: IngestResource,
        stats: RelivioStatsStore,
        *,
        default_service: Optional[str] = None,
        trace_id_provider: Optional[TraceIdProvider] = None,
    ) -> None:
        self._ingest = ingest
        self._stats = stats
        self._default_service = default_service
        self._trace_id_provider = trace_id_provider

    def capture_exception(
        self,
        exc: BaseException,
        *,
        service: Optional[str] = None,
        level: LogLevel = "ERROR",
        api_path: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> None:
        input = CaptureExceptionInput(
            exception=exc,
            service=service if service is not None else self._default_service,
            level=level,
            api_path=api_path,
            trace_id=trace_id if trace_id is not None else self._resolve_trace_id(),
        )
        self._capture(input, async_send=False)

    async def acapture_exception(
        self,
        exc: BaseException,
        *,
        service: Optional[str] = None,
        level: LogLevel = "ERROR",
        api_path: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> None:
        input = CaptureExceptionInput(
            exception=exc,
            service=service if service is not None else self._default_service,
            level=level,
            api_path=api_path,
            trace_id=trace_id if trace_id is not None else self._resolve_trace_id(),
        )
        await self._acapture(input)

    def _resolve_trace_id(self) -> Optional[str]:
        provider = self._trace_id_provider
        if provider is None:
            return None
        try:
            value = provider()
        except Exception:
            return None
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        return value or None

    def _build_ingest_input(self, input: CaptureExceptionInput) -> IngestLogInput:
        exc = input.exception
        stacktrace = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
        return IngestLogInput(
            level=input.level,
            message=str(exc) or type(exc).__name__,
            stacktrace=stacktrace,
            service=input.service,
            api_path=input.api_path,
            trace_id=input.trace_id,
            error_type=type(exc).__name__,
        )

    def _capture(self, input: CaptureExceptionInput, *, async_send: bool) -> None:
        if async_send:
            raise ValueError("async capture must use _acapture")
        self._stats.record_captured_event()
        try:
            self._ingest.send(self._build_ingest_input(input))
        except Exception as send_error:  # pragma: no cover - defensive boundary
            self._stats.record_capture_send_failure(send_error)

    async def _acapture(self, input: CaptureExceptionInput) -> None:
        self._stats.record_captured_event()
        try:
            await self._ingest.asend(self._build_ingest_input(input))
        except Exception as send_error:  # pragma: no cover - defensive boundary
            self._stats.record_capture_send_failure(send_error)
