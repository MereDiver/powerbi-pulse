"""Optional, generic PAC proxy support for PULSE."""

from __future__ import annotations

import os
from typing import Mapping

import requests


POWER_BI_API_URL = "https://api.powerbi.com/v1.0/myorg/groups"
_PROXY_ENV_KEYS = {"http": "HTTP_PROXY", "https": "HTTPS_PROXY"}
_original_environment: dict[str, str | None] = {}


def configure_pac_proxy(
    target_url: str = POWER_BI_API_URL,
    *,
    timeout_seconds: float = 10,
) -> dict[str, str]:
    """Discover a PAC file, verify transport, and expose its proxies to clients.

    Any HTTP response proves that the proxy transport reached the API. The endpoint
    requires authentication, so an unauthenticated 401/403 is not a proxy failure.
    """
    try:
        from pypac import get_pac
        from pypac.resolver import ProxyResolver
    except ImportError as exc:
        raise RuntimeError(
            "PAC mode requires PyPAC. Install the dependencies from requirements.txt."
        ) from exc

    pac = get_pac()
    if pac is None:
        raise RuntimeError("No PAC configuration could be discovered on this system")

    proxies = {
        key: value
        for key, value in ProxyResolver(pac).get_proxy_for_requests(target_url).items()
        if key in _PROXY_ENV_KEYS and value
    }
    if not proxies:
        raise RuntimeError("The discovered PAC did not provide an HTTP or HTTPS proxy")

    try:
        requests.get(target_url, timeout=timeout_seconds, proxies=proxies)
    except requests.RequestException as exc:
        raise RuntimeError(f"The PAC proxy could not reach the Power BI API: {exc}") from exc

    _apply_proxy_environment(proxies)
    return proxies


def _apply_proxy_environment(proxies: Mapping[str, str]) -> None:
    for scheme, value in proxies.items():
        env_key = _PROXY_ENV_KEYS.get(scheme.casefold())
        if not env_key:
            continue
        if env_key not in _original_environment:
            _original_environment[env_key] = os.environ.get(env_key)
        os.environ[env_key] = value


def restore_proxy_environment() -> None:
    """Restore only proxy variables previously changed by this module."""
    for key, original_value in _original_environment.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value
    _original_environment.clear()

