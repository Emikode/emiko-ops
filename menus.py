"""
Menus — all Telegram InlineKeyboard layouts.

Keeps UI separate from bot handler logic.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ── Main menu ────────────────────────────────────────────────

def main_menu() -> tuple[str, InlineKeyboardMarkup]:
    text = "🤖 *Emiko Ops*"
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Systems", callback_data="menu:systems")],
        [InlineKeyboardButton("🚀 Deploy", callback_data="menu:deploy")],
        [InlineKeyboardButton("💚 Health", callback_data="menu:health")],
        [InlineKeyboardButton("📜 Logs", callback_data="menu:logs")],
        [InlineKeyboardButton("🧠 Claude Assistant", callback_data="menu:claude")],
    ])
    return text, buttons


# ── Systems list ─────────────────────────────────────────────

def systems_menu() -> tuple[str, InlineKeyboardMarkup]:
    text = "📋 *Systems*\nSelect a system to manage:"
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🐍 PythonFX", callback_data="system:pythonfx")],
        [InlineKeyboardButton("⬅ Back", callback_data="menu:main")],
    ])
    return text, buttons


# ── PythonFX dashboard ──────────────────────────────────────

def pythonfx_dashboard(status: dict) -> tuple[str, InlineKeyboardMarkup]:
    error_line = ""
    if status.get("error"):
        error_line = f"⚠ _{status['error']}_\n\n"

    text = (
        f"🐍 *PythonFX*\n\n"
        f"{error_line}"
        "SYSTEM STATUS\n"
        f"• Forwarder: {status['forwarder_status']}\n"
        f"• Outreach: {status['outreach_status']}\n"
        f"• Signals today: {status['signals_today']}\n"
        f"• Last signal: {status['last_signal_time']}\n\n"
        "COMMUNITY\n"
        f"• Free members: {status['free_members']}\n"
        f"• VIP members: {status['vip_members']}"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="system:pythonfx")],
        [InlineKeyboardButton("🛠 Restart Forwarder", callback_data="pfx:restart:forwarder")],
        [InlineKeyboardButton("📣 Restart Outreach", callback_data="pfx:restart:outreach")],
        [InlineKeyboardButton("📜 View Logs", callback_data="pfx:logs")],
        [InlineKeyboardButton("🚀 Deploy Latest Version", callback_data="pfx:deploy")],
        [InlineKeyboardButton("⬅ Back", callback_data="menu:systems")],
    ])
    return text, buttons


# ── Logs screen ──────────────────────────────────────────────

def logs_screen(log_text: str) -> tuple[str, InlineKeyboardMarkup]:
    truncated = log_text[:3500]
    if len(log_text) > 3500:
        truncated += "\n... (truncated)"
    text = f"📜 *Recent Logs*\n\n```\n{truncated}\n```"
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="pfx:logs")],
        [InlineKeyboardButton("⬅ Back", callback_data="system:pythonfx")],
    ])
    return text, buttons


# ── Claude Assistant mode ────────────────────────────────────

def claude_mode_screen() -> tuple[str, InlineKeyboardMarkup]:
    text = (
        "🧠 *Claude Assistant*\n\n"
        "I'm Emiko, your AI operations engineer. "
        "Ask me anything about your systems.\n\n"
        "_Try asking:_\n"
        '• "Why did signals stop?"\n'
        '• "Is outreach running?"\n'
        '• "Show latest logs"\n'
        '• "Preview the DM template"\n'
        '• "Improve the Instagram content template"'
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Exit Claude Mode", callback_data="claude:exit")],
    ])
    return text, buttons


def claude_response_buttons(actions: list[dict]) -> InlineKeyboardMarkup:
    """Build buttons for a Claude response: action suggestions + exit."""
    rows = []
    for action in actions:
        rows.append(
            [InlineKeyboardButton(action["label"], callback_data=action["callback"])]
        )
    rows.append([InlineKeyboardButton("❌ Exit Claude Mode", callback_data="claude:exit")])
    return InlineKeyboardMarkup(rows)


# ── Operator analysis screen ────────────────────────────────

def operator_analysis(text: str, actions: list[dict]) -> tuple[str, InlineKeyboardMarkup]:
    action_buttons = []
    for action in actions:
        action_buttons.append(
            [InlineKeyboardButton(action["label"], callback_data=action["callback"])]
        )
    action_buttons.append(
        [InlineKeyboardButton("⬅ Back", callback_data="menu:main")]
    )
    display = f"🧠 *Operator Analysis*\n\n{text}"
    buttons = InlineKeyboardMarkup(action_buttons)
    return display, buttons


# ── Placeholder screens ─────────────────────────────────────

def placeholder_screen(title: str) -> tuple[str, InlineKeyboardMarkup]:
    text = f"*{title}*\n\nComing soon."
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Back", callback_data="menu:main")],
    ])
    return text, buttons
