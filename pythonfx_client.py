"""
PythonFX Client — talks to PythonFX's health endpoint.

Will fetch live status from PythonFX's own API once
a /health endpoint is exposed. Until then, returns placeholders.

This does NOT contain any trading or automation logic —
it only reads status data that PythonFX exposes.
"""

from utils.logger import log

# TODO: set via .env once PythonFX health endpoint is live
PYTHONFX_BASE_URL = None


def get_status() -> dict:
    """Fetch service statuses from PythonFX health endpoint."""
    log.info("pythonfx: status requested (placeholder)")
    return {
        "forwarder": "Running",
        "tg_outreach": "Running",
        "ig_outreach": "Running",
        "education_generator": "Running",
    }


def get_members() -> dict:
    """Fetch member counts from PythonFX."""
    log.info("pythonfx: members requested (placeholder)")
    return {
        "free": "unknown",
        "vip": "unknown",
    }


def get_logs(service: str = "all", lines: int = 20) -> str:
    """Fetch recent logs from PythonFX."""
    log.info("pythonfx: logs requested for %s (placeholder)", service)
    return f"[placeholder] No live logs for {service}. Connect PythonFX health endpoint to enable."
