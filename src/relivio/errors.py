from typing import Optional


class RelivioError(Exception):
    """Base SDK error."""


class RelivioApiError(RelivioError):
    def __init__(
        self,
        message: str,
        status: int,
        code: str,
        request_id: Optional[str],
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.request_id = request_id


class RelivioTimeoutError(RelivioError):
    def __init__(self, timeout_s: float) -> None:
        super().__init__(f"Request timed out after {timeout_s}s")
        self.timeout_s = timeout_s


class RelivioNetworkError(RelivioError):
    def __init__(self, cause: Optional[Exception] = None) -> None:
        super().__init__("Network request failed")
        self.cause = cause
