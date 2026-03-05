"""
Claude Assistant — AI operations engineer powered by Anthropic API.

Provides conversational assistance, health analysis, and
safe action suggestions for the Emiko Ops control tower.
"""

import os

import anthropic

from utils.logger import log

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 800
TEMPERATURE = 0.2


def _get_api_key() -> str | None:
    """Read API key at call time, not import time."""
    return os.getenv("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = (
    "You are Emiko, an AI operations engineer for a Telegram-based control tower. "
    "You manage PythonFX (an automated trading/signal system) and Emiko Ops itself. "
    "You can help with: system health, logs, deployments, debugging, code changes, "
    "UI/UX suggestions, architecture decisions, bug fixes, feature planning, "
    "template previews, configuration, and anything the CEO needs from mobile.\n\n"
    "Be concise — keep responses short and clear for Telegram.\n\n"
    "When you recommend an action, use these exact phrases so the system can "
    "generate action buttons:\n"
    "- 'restart forwarder' — restart the signal forwarder\n"
    "- 'restart outreach' — restart the outreach bot\n"
    "- 'view logs' — show recent logs\n"
    "- 'deploy' — deploy the latest version\n"
    "- 'refresh status' — refresh the health dashboard\n"
)

# Approved actions that map to callback buttons
ACTION_MAP = {
    "restart forwarder": {"label": "🛠 Restart Forwarder", "callback": "pfx:restart:forwarder"},
    "restart outreach": {"label": "📣 Restart Outreach", "callback": "pfx:restart:outreach"},
    "view logs": {"label": "📜 View Logs", "callback": "pfx:logs"},
    "deploy": {"label": "🚀 Deploy Latest", "callback": "pfx:deploy"},
    "refresh status": {"label": "🔄 Refresh Status", "callback": "system:pythonfx"},
}


def _build_health_context(health_data: dict | None) -> str:
    if not health_data:
        return "No health data available."
    lines = ["Current PythonFX status:"]
    for key, value in health_data.items():
        if key != "error":
            lines.append(f"  {key}: {value}")
    if health_data.get("error"):
        lines.append(f"  ⚠ Error: {health_data['error']}")
    return "\n".join(lines)


def extract_actions(text: str) -> list[dict]:
    """Scan text for approved action keywords and return matching buttons."""
    actions = []
    text_lower = text.lower()
    for keyword, action in ACTION_MAP.items():
        if keyword in text_lower and action not in actions:
            actions.append(action)
    return actions


async def ask_claude(
    user_message: str,
    conversation_history: list[dict] | None = None,
    health_data: dict | None = None,
) -> str:
    """Send a message to Claude with system context and conversation history."""
    api_key = _get_api_key()
    if not api_key:
        return "Claude is not connected. Set ANTHROPIC_API_KEY to enable."

    try:
        client = anthropic.AsyncAnthropic(api_key=api_key)

        system = SYSTEM_PROMPT + "\n\n" + _build_health_context(health_data)

        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        response = await client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=system,
            messages=messages,
        )

        return response.content[0].text

    except anthropic.AuthenticationError:
        log.error("claude: invalid API key")
        return "⚠ Claude API key is invalid. Check ANTHROPIC_API_KEY."
    except anthropic.RateLimitError:
        log.error("claude: rate limited")
        return "⚠ Rate limited. Try again in a moment."
    except Exception as e:
        log.error("claude: unexpected error — %s: %s", type(e).__name__, e)
        return f"⚠ Claude error: {type(e).__name__}: {e}"


async def analyze_health(health_data: dict) -> tuple[str, list[dict]]:
    """Operator mode — analyze health data and suggest actions."""
    api_key = _get_api_key()
    if not api_key:
        return "Claude is not connected. Set ANTHROPIC_API_KEY to enable.", []

    try:
        client = anthropic.AsyncAnthropic(api_key=api_key)

        health_context = _build_health_context(health_data)
        prompt = (
            f"{health_context}\n\n"
            "Analyze this system health data. Provide:\n"
            "1. A brief status summary (2-3 sentences)\n"
            "2. Any concerns or issues\n"
            "3. Recommended actions (use exact phrases: "
            "'restart forwarder', 'restart outreach', 'view logs', 'deploy', 'refresh status')"
        )

        response = await client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        analysis_text = response.content[0].text
        actions = extract_actions(analysis_text)

        return analysis_text, actions

    except Exception as e:
        log.error("claude: analyze_health error — %s: %s", type(e).__name__, e)
        return f"⚠ Claude error: {type(e).__name__}: {e}", []
