"""
Telegram Bot — handler wiring and callback routing.

All user interactions flow through here. Menu rendering is
delegated to menus.py; external calls go through the clients.
"""

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import menus
import railway_client
import pythonfx_client
from ai.claude_assistant import ask_claude, analyze_health, extract_actions
from utils.logger import log


# ── Command handlers ────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text, buttons = menus.main_menu()
    await update.message.reply_text(text, reply_markup=buttons, parse_mode="Markdown")


# ── Text message handler (Claude mode) ─────────────────────

async def on_text_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.user_data.get("claude_mode"):
        return

    user_msg = update.message.text
    await update.message.chat.send_action("typing")

    # Get health context
    health_data = pythonfx_client.get_pythonfx_status()

    # Get conversation history
    history = ctx.user_data.get("claude_history", [])

    response = await ask_claude(user_msg, history, health_data)

    # Store conversation history (capped at 20 messages)
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": response})
    if len(history) > 20:
        history = history[-20:]
    ctx.user_data["claude_history"] = history

    # Detect suggested actions and build buttons
    actions = extract_actions(response)
    reply_markup = menus.claude_response_buttons(actions)

    # Try Markdown first, fall back to plain text
    try:
        await update.message.reply_text(
            response,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    except Exception:
        await update.message.reply_text(
            response,
            reply_markup=reply_markup,
        )


# ── Callback router ────────────────────────────────────────

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # --- navigation menus ---
    if data == "menu:main":
        ctx.user_data["claude_mode"] = False
        text, buttons = menus.main_menu()

    elif data == "menu:systems":
        text, buttons = menus.systems_menu()

    elif data == "menu:deploy":
        text, buttons = menus.placeholder_screen("🚀 Deploy")

    elif data == "menu:health":
        text, buttons = menus.placeholder_screen("💚 Health")

    elif data == "menu:logs":
        text, buttons = menus.placeholder_screen("📜 Logs")

    elif data == "menu:claude":
        ctx.user_data["claude_mode"] = True
        ctx.user_data["claude_history"] = []
        text, buttons = menus.claude_mode_screen()

    elif data == "claude:exit":
        ctx.user_data["claude_mode"] = False
        text, buttons = menus.main_menu()

    elif data == "menu:settings":
        text, buttons = menus.placeholder_screen("⚙ Settings")

    # --- PythonFX dashboard ---
    elif data == "system:pythonfx":
        status = pythonfx_client.get_pythonfx_status()
        text, buttons = menus.pythonfx_dashboard(status)

    # --- PythonFX actions ---
    elif data.startswith("pfx:restart:"):
        service = data.split(":")[-1]
        try:
            result = railway_client.restart_service(service)
        except Exception as e:
            log.error("pfx restart error: %s", e)
            result = "⚠ Restart failed. Check logs."
        status = pythonfx_client.get_pythonfx_status()
        dash_text, buttons = menus.pythonfx_dashboard(status)
        text = f"_{result}_\n\n{dash_text}"

    elif data == "pfx:logs":
        log_text = pythonfx_client.get_recent_logs()
        text, buttons = menus.logs_screen(log_text)

    elif data == "pfx:deploy":
        try:
            result = railway_client.deploy_latest()
        except Exception as e:
            log.error("pfx deploy error: %s", e)
            result = "⚠ Deploy failed. Check logs."
        status = pythonfx_client.get_pythonfx_status()
        dash_text, buttons = menus.pythonfx_dashboard(status)
        text = f"_{result}_\n\n{dash_text}"

    else:
        text, buttons = menus.main_menu()

    # Try Markdown first, fall back to plain text
    try:
        await query.edit_message_text(text, reply_markup=buttons, parse_mode="Markdown")
    except Exception:
        await query.edit_message_text(text, reply_markup=buttons)


# ── Error handler ───────────────────────────────────────────

async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    log.error("Unhandled exception: %s", ctx.error)
    if update and hasattr(update, "effective_message") and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠ System error occurred.\nCheck logs for details."
            )
        except Exception:
            pass


# ── Bot factory ─────────────────────────────────────────────

def create_bot(token: str) -> Application:
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text_message))
    app.add_error_handler(error_handler)
    log.info("Telegram bot handlers registered")
    return app
