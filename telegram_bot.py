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
)

import menus
import railway_client
import pythonfx_client
from ai.claude_assistant import ask_claude
from utils.logger import log


# ── Command handlers ────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text, buttons = menus.main_menu()
    await update.message.reply_text(text, reply_markup=buttons, parse_mode="Markdown")


# ── Callback router ────────────────────────────────────────

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # --- navigation menus ---
    if data == "menu:main":
        text, buttons = menus.main_menu()

    elif data == "menu:systems":
        text, buttons = menus.systems_menu()

    elif data == "menu:deploy":
        text, buttons = menus.placeholder_screen("Deploy")

    elif data == "menu:health":
        text, buttons = menus.placeholder_screen("Health")

    elif data == "menu:logs":
        text, buttons = menus.placeholder_screen("Logs")

    elif data == "menu:claude":
        text, buttons = menus.placeholder_screen("Claude Assistant")

    elif data == "menu:settings":
        text, buttons = menus.placeholder_screen("Settings")

    # --- PythonFX dashboard ---
    elif data == "system:pythonfx":
        status = pythonfx_client.get_pythonfx_status()
        text, buttons = menus.pythonfx_dashboard(status)

    # --- PythonFX actions ---
    elif data.startswith("pfx:restart:"):
        service = data.split(":")[-1]
        result = railway_client.restart_service(service)
        status = pythonfx_client.get_pythonfx_status()
        dash_text, buttons = menus.pythonfx_dashboard(status)
        text = f"_{result}_\n\n{dash_text}"

    elif data == "pfx:logs":
        result = pythonfx_client.get_logs()
        status = pythonfx_client.get_pythonfx_status()
        dash_text, buttons = menus.pythonfx_dashboard(status)
        text = f"`{result}`\n\n{dash_text}"

    elif data == "pfx:deploy":
        result = railway_client.deploy_latest()
        status = pythonfx_client.get_pythonfx_status()
        dash_text, buttons = menus.pythonfx_dashboard(status)
        text = f"_{result}_\n\n{dash_text}"

    else:
        text, buttons = menus.main_menu()

    await query.edit_message_text(text, reply_markup=buttons, parse_mode="Markdown")


# ── Bot factory ─────────────────────────────────────────────

def create_bot(token: str) -> Application:
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(on_callback))
    log.info("Telegram bot handlers registered")
    return app
