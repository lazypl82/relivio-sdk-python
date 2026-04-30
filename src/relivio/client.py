from .capture import CaptureResource
from .http import HttpTransport
from .resources.protection import ProtectionResource
from .resources.deployments import DeploymentsResource
from .resources.ingest import IngestResource
from .resources.verdicts import VerdictsResource
from .stats import RelivioStatsSnapshot, RelivioStatsStore
from .types.options import RelivioOptions, resolve_options


class Relivio:
    def __init__(self, api_key: str, **kwargs):
        options = resolve_options(RelivioOptions(api_key=api_key, **kwargs))
        http = HttpTransport(options)
        self._stats_store = RelivioStatsStore()
        self.deployments = DeploymentsResource(http)
        self.ingest = IngestResource(http)
        self.protection = ProtectionResource(http)
        self.verdicts = VerdictsResource(http)
        self.capture = CaptureResource(self.ingest, self._stats_store)

    def status(self) -> RelivioStatsSnapshot:
        return self._stats_store.snapshot()

    def stats(self) -> RelivioStatsSnapshot:
        return self.status()

    def capture_exception(self, *args, **kwargs) -> None:
        self.capture.capture_exception(*args, **kwargs)

    async def acapture_exception(self, *args, **kwargs) -> None:
        await self.capture.acapture_exception(*args, **kwargs)
