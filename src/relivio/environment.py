from __future__ import annotations

import json
import os
import platform
import socket
from pathlib import Path
from typing import Dict, Optional


def collect_deployment_metadata(
    cwd: Optional[str] = None,
    *,
    include_hostname: bool = False,
) -> Dict[str, str]:
    metadata: Dict[str, str] = {
        "runtime": "python",
        "runtime_version": platform.python_version(),
        "os_platform": platform.system().lower(),
        "os_arch": platform.machine(),
    }

    pyproject = _read_pyproject_name_version(Path(cwd or os.getcwd()) / "pyproject.toml")
    if pyproject.get("name"):
        metadata["package_name"] = pyproject["name"]
    if pyproject.get("version"):
        metadata["package_version"] = pyproject["version"]

    commit_sha = _first_env_value(
        [
            "RELIVIO_COMMIT_SHA",
            "GITHUB_SHA",
            "VERCEL_GIT_COMMIT_SHA",
            "RAILWAY_GIT_COMMIT_SHA",
            "COMMIT_SHA",
            "GIT_SHA",
        ]
    )
    if commit_sha:
        metadata["commit_sha"] = commit_sha

    image_digest = _first_env_value(
        [
            "RELIVIO_IMAGE_DIGEST",
            "IMAGE_DIGEST",
            "CONTAINER_IMAGE_DIGEST",
        ]
    )
    if image_digest:
        metadata["image_digest"] = image_digest

    environment = _first_env_value(
        [
            "RELIVIO_ENV",
            "DEPLOY_ENV",
            "PYTHON_ENV",
            "ENVIRONMENT",
        ]
    )
    if environment:
        metadata["environment"] = environment

    if include_hostname:
        metadata["hostname"] = socket.gethostname()

    return metadata


def _first_env_value(keys: list[str]) -> Optional[str]:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return None


def _read_pyproject_name_version(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    return _parse_project_name_version(content)


def _parse_project_name_version(content: str) -> Dict[str, str]:
    in_project = False
    values: Dict[str, str] = {}

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_project = line == "[project]"
            continue
        if not in_project or "=" not in line:
            continue
        key, raw_value = [part.strip() for part in line.split("=", 1)]
        if key not in {"name", "version"}:
            continue
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError:
            continue
        if isinstance(value, str):
            values[key] = value

    return values
