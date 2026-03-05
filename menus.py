"""
Menus — all Telegram InlineKeyboard layouts.

Keeps UI separate from bot handler logic.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ── Main menu ────────────────────────────────────────────────

def main_menu() -> tuple[str, InlineKeyboardMarkup]:
    text = "**Emiko Ops Control Tower**"
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Systems", callback_data="menu:systems")],
        [InlineKeyboardButton("Deploy", callback_data="menu:deploy")],
        [InlineKeyboardButton("Health", callback_data="menu:health")],
        [InlineKeyboardButton("Logs", callback_data="menu:logs")],
        [InlineKeyboardButton("Claude Assistant", callback_data="menu:claude")],
        [InlineKeyboardButton("Settings", callback_data="menu:settings")],
    ])
    return text, buttons


# ── Systems list ─────────────────────────────────────────────

def systems_menu() -> tuple[str, InlineKeyboardMarkup]:
    text = "**Systems**\nSelect a system to manage:"
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("PythonFX", callback_data="system:pythonfx")],
        [InlineKeyboardButton("Back", callback_data="menu:main")],
    ])
    return text, buttons


# ── PythonFX dashboard ──────────────────────────────────────

def pythonfx_dashboard(status: dict) -> tuple[str, InlineKeyboardMarkup]:
    error_line = ""
    if status.get("error"):
        error_line = f"\n⚠ {status['error']}\n"

    text = (
        "**PythonFX Dashboard**\n"
        f"{error_line}\n"
        f"Forwarder: {status['forwarder_status']}\n"
        f"Outreach: {status['outreach_status']}\n"
        f"Signals today: {status['signals_today']}\n"
        f"Last signal: {status['last_signal_time']}\n\n"
        f"Free members: {status['free_members']}\n"
        f"VIP members: {status['vip_members']}"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Refresh", callback_data="system:pythonfx")],
        [InlineKeyboardButton("Restart Forwarder", callback_data="pfx:restart:forwarder")],
        [InlineKeyboardButton("Restart Outreach", callback_data="pfx:restart:outreach")],
        [InlineKeyboardButton("View Logs", callback_data="pfx:logs")],
        [InlineKeyboardButton("Deploy Latest Version", callback_data="pfx:deploy")],
        [InlineKeyboardButton("Back", callback_data="menu:systems")],
    ])
    return text, buttons


# ── Placeholder screens ─────────────────────────────────────

def placeholder_screen(title: str) -> tuple[str, InlineKeyboardMarkup]:
    text = f"**{title}**\n\nComing soon."
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data="menu:main")],
    ])
    return text, buttons
