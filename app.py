"""
Emiko Ops — entry point.

Loads config and starts the Telegram bot in polling mode.
"""

import os
from dotenv import load_dotenv
from telegram_bot import create_bot
from utils.logger import log


def main():
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        log.error("TELEGRAM_BOT_TOKEN not set. Copy .env.example to .env and fill it in.")
        return

    log.info("Starting Emiko Ops...")
    bot = create_bot(token)
    bot.run_polling()


if __name__ == "__main__":
    main()
