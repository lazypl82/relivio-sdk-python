from dataclasses import dataclass
from typing import Callable, Optional


TraceIdProvider = Callable[[], Optional[str]]


@dataclass(frozen=True)
class RelivioOptions:
    api_key: str
    base_url: str = "https://api.relivio.dev"
    timeout_s: float = 2.0
    max_retries: int = 3
    async_mode: bool = False
    default_service: Optional[str] = None
    trace_id_provider: Optional[TraceIdProvider] = None


@dataclass(frozen=True)
class ResolvedOptions:
    api_key: str
    base_url: str
    timeout_s: float
    max_retries: int
    async_mode: bool
    default_service: Optional[str]
    trace_id_provider: Optional[TraceIdProvider]


def resolve_options(options: RelivioOptions) -> ResolvedOptions:
    api_key = options.api_key.strip()
    if not api_key:
        raise ValueError("api_key is required")

    base_url = options.base_url.strip().rstrip("/")
    if not base_url:
        raise ValueError("base_url must be non-empty")

    if options.timeout_s <= 0:
        raise ValueError("timeout_s must be positive")
    if options.max_retries < 0:
        raise ValueError("max_retries must be >= 0")

    default_service = (
        options.default_service.strip() or None
        if isinstance(options.default_service, str)
        else None
    )

    return ResolvedOptions(
        api_key=api_key,
        base_url=base_url,
        timeout_s=options.timeout_s,
        max_retries=options.max_retries,
        async_mode=options.async_mode,
        default_service=default_service,
        trace_id_provider=options.trace_id_provider,
    )
