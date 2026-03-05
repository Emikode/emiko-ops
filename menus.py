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

def pythonfx_dashboard(status: dict, members: dict) -> tuple[str, InlineKeyboardMarkup]:
    text = (
        "**PythonFX Dashboard**\n\n"
        f"Forwarder: {status['forwarder']}\n"
        f"TG Outreach: {status['tg_outreach']}\n"
        f"IG Outreach: {status['ig_outreach']}\n"
        f"Education Generator: {status['education_generator']}\n\n"
        f"Free members: {members['free']}\n"
        f"VIP members: {members['vip']}"
    )
    buttons = InlineKeyboardMarkup([
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
