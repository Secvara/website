#!/usr/bin/env python3
"""
Shared helpers for Google platform automation scripts using YAML configuration.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import json
import yaml
from google.auth.transport.requests import Request
from google.oauth2 import credentials as oauth_credentials
from google.oauth2 import service_account


TOKEN_URI = "https://oauth2.googleapis.com/token"
CONFIG_ENV_VAR = "GOOGLE_TOOL_CONFIG"
CONFIG_DEFAULT_PATH = Path(__file__).resolve().parent / "config.yaml"


class ConfigError(RuntimeError):
    """Raised when required configuration values are missing."""


@lru_cache(maxsize=1)
def load_config() -> Mapping[str, object]:
    """Load the YAML configuration once."""
    config_path = Path(os.getenv(CONFIG_ENV_VAR, CONFIG_DEFAULT_PATH))
    if not config_path.exists():
        raise ConfigError(
            f"Config file not found at {config_path}. Run scripts/google/configure.py "
            "to generate it, add your secrets, then rerun."
        )
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ConfigError("Config file must contain a YAML mapping at the top level.")
    return data


def _walk_config(path: Sequence[str]) -> object | None:
    """Traverse the config dict following dotted notation."""
    node: object = load_config()
    for part in path:
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def require_values(paths: Sequence[str]) -> Mapping[str, object]:
    """Ensure each dotted path has a non-empty value and return the mapping."""
    resolved = {}
    missing = []
    for path in paths:
        parts = path.split(".")
        value = _walk_config(parts)
        if value is None or value == "":
            missing.append(path)
        else:
            resolved[path] = value
    if missing:
        joined = ", ".join(missing)
        raise ConfigError(f"Missing required configuration values: {joined}")
    return resolved


def get_value(path: str, default: object | None = None) -> object | None:
    """Fetch an optional value from the config using dotted notation."""
    parts = path.split(".")
    value = _walk_config(parts)
    if value is None or value == "":
        return default
    return value


def quota_project() -> str | None:
    """Return the quota project configured for API calls, if any."""
    value = get_value("quota_project")
    return str(value) if value else None


def user_credentials(scopes: Iterable[str]) -> oauth_credentials.Credentials:
    """Build OAuth user credentials using the oauth section."""
    oauth_section = load_config().get("oauth", {})
    client_id = oauth_section.get("client_id")
    client_secret = oauth_section.get("client_secret")
    refresh_token = oauth_section.get("refresh_token")
    secrets_file = oauth_section.get("client_secrets_file")

    if secrets_file:
        secrets_path = Path(str(secrets_file)).expanduser()
        if secrets_path.exists():
            with secrets_path.open("r", encoding="utf-8") as handle:
                client_json = json.load(handle)
            descriptor = client_json.get("installed") or client_json.get("web") or {}
            client_id = client_id or descriptor.get("client_id")
            client_secret = client_secret or descriptor.get("client_secret")

    missing = []
    if not client_id:
        missing.append("oauth.client_id")
    if not client_secret:
        missing.append("oauth.client_secret")
    if not refresh_token:
        missing.append("oauth.refresh_token")
    if missing:
        raise ConfigError(f"Missing required configuration values: {', '.join(missing)}")

    creds = oauth_credentials.Credentials(
        token=None,
        refresh_token=str(refresh_token),
        token_uri=TOKEN_URI,
        client_id=str(client_id),
        client_secret=str(client_secret),
        scopes=list(scopes),
    )
    creds.refresh(Request())
    return creds


def service_account_credentials(scopes: Iterable[str]) -> service_account.Credentials:
    """Build service-account credentials using the project section."""
    required = require_values(["project.service_account_key"])
    credentials = service_account.Credentials.from_service_account_file(
        Path(str(required["project.service_account_key"])), scopes=list(scopes)
    )
    quota = quota_project()
    if quota:
        credentials = credentials.with_quota_project(quota)
    return credentials
