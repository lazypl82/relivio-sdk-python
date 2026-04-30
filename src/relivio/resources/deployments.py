from typing import Dict, Optional

from ..environment import collect_deployment_metadata
from ..http import HttpTransport
from ..types.deployments import (
    RegisterDeploymentInput,
    RegisterDeploymentResponse,
)


class DeploymentsResource:
    def __init__(self, http: HttpTransport):
        self._http = http

    def register(
        self,
        input: Optional[RegisterDeploymentInput] = None,
    ) -> RegisterDeploymentResponse:
        payload = _build_wire_body(input)
        raw = self._http.request(
            method="POST",
            path="/api/v1/deployments",
            body=payload,
            idempotency_key=input.idempotency_key if input else None,
        )
        return RegisterDeploymentResponse(
            id=str(raw["id"]),
            version=raw.get("version") if isinstance(raw.get("version"), str) else None,
            summary_scheduled=bool(raw["summary_scheduled"]),
        )

    def register_from_environment(
        self,
        input: Optional[RegisterDeploymentInput] = None,
    ) -> RegisterDeploymentResponse:
        payload_input = _with_environment_metadata(input)
        return self.register(payload_input)

    async def aregister(
        self,
        input: Optional[RegisterDeploymentInput] = None,
    ) -> RegisterDeploymentResponse:
        payload = _build_wire_body(input)
        raw = await self._http.arequest(
            method="POST",
            path="/api/v1/deployments",
            body=payload,
            idempotency_key=input.idempotency_key if input else None,
        )
        return RegisterDeploymentResponse(
            id=str(raw["id"]),
            version=raw.get("version") if isinstance(raw.get("version"), str) else None,
            summary_scheduled=bool(raw["summary_scheduled"]),
        )

    async def aregister_from_environment(
        self,
        input: Optional[RegisterDeploymentInput] = None,
    ) -> RegisterDeploymentResponse:
        payload_input = _with_environment_metadata(input)
        return await self.aregister(payload_input)


def _build_wire_body(
    input: Optional[RegisterDeploymentInput],
) -> Dict[str, object]:
    return {
        "version": input.version if input else None,
        "note": input.note if input else None,
        "metadata": input.metadata if input else None,
    }


def _with_environment_metadata(
    input: Optional[RegisterDeploymentInput],
) -> RegisterDeploymentInput:
    metadata = collect_deployment_metadata()
    if input and input.metadata:
        metadata.update(input.metadata)

    version = (
        input.version
        if input and input.version
        else metadata.get("commit_sha") or metadata.get("package_version")
    )

    return RegisterDeploymentInput(
        version=version,
        note=input.note if input else None,
        metadata=metadata,
        idempotency_key=input.idempotency_key if input else None,
    )
