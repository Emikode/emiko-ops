"""
PythonFX Client — reads status from PythonFX's /health endpoint.

This does NOT contain any trading or automation logic —
it only reads status data that PythonFX exposes.
"""

import os

import requests

from utils.logger import log

PYTHONFX_BASE_URL = os.getenv("PYTHONFX_BASE_URL")
REQUEST_TIMEOUT = 10


def get_pythonfx_status() -> dict:
    """Fetch live status from PythonFX /health endpoint.

    Returns a dict with display-ready fields. On failure returns
    the same structure with error placeholders so the UI always works.
    """
    if not PYTHONFX_BASE_URL:
        log.warning("PYTHONFX_BASE_URL not set — returning offline status")
        return _offline_status("PYTHONFX_BASE_URL not configured")

    url = f"{PYTHONFX_BASE_URL.rstrip('/')}/health"
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        log.info("pythonfx: health endpoint responded OK")
        return {
            "forwarder_status": data.get("forwarder_status", "unknown"),
            "signals_today": data.get("signals_today", "unknown"),
            "free_members": data.get("free_members", "unknown"),
            "vip_members": data.get("vip_members", "unknown"),
            "outreach_status": data.get("outreach_status", "unknown"),
            "last_signal_time": data.get("last_signal_time", "unknown"),
        }
    except requests.ConnectionError:
        log.error("pythonfx: connection refused — is PythonFX running?")
        return _offline_status("Connection refused")
    except requests.Timeout:
        log.error("pythonfx: health endpoint timed out after %ds", REQUEST_TIMEOUT)
        return _offline_status("Request timed out")
    except requests.HTTPError as e:
        log.error("pythonfx: health endpoint returned %s", e.response.status_code)
        return _offline_status(f"HTTP {e.response.status_code}")
    except (ValueError, KeyError) as e:
        log.error("pythonfx: bad response from health endpoint — %s", e)
        return _offline_status("Invalid response format")


def _offline_status(reason: str) -> dict:
    """Return a safe fallback dict when PythonFX is unreachable."""
    return {
        "forwarder_status": "unreachable",
        "signals_today": "—",
        "free_members": "—",
        "vip_members": "—",
        "outreach_status": "unreachable",
        "last_signal_time": "—",
        "error": reason,
    }


def get_logs(service: str = "all", lines: int = 20) -> str:
    """Fetch recent logs from PythonFX. Placeholder until log endpoint exists."""
    log.info("pythonfx: logs requested for %s (placeholder)", service)
    return f"[placeholder] No live logs for {service}. Connect PythonFX log endpoint to enable."
