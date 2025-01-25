import logging
import os
import sys
from datetime import datetime

from loguru import logger
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .commands import print_help, set_stare, set_zoomstare, start
from .pipeline import take_photo, take_sticker

logging.getLogger("telegram").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

logger.remove()
logger.add(f"logs/{datetime.now():%Y-%m}.log", rotation="1 month", level="INFO")
logger.add(sys.stderr, level="INFO")


def main():
    telegram_token = os.getenv("TELEGRAM_TOKEN", "")
    app = Application.builder().token(telegram_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", print_help))
    app.add_handler(MessageHandler(filters.PHOTO, take_photo))
    app.add_handler(MessageHandler(filters.Sticker.STATIC, take_sticker))
    app.add_handler(CommandHandler("stare", set_stare))
    app.add_handler(CommandHandler("zoomstare", set_zoomstare))

    logger.info("starting intensifyer bot")
    app.run_polling(allowed_updates=[Update.MESSAGE])


if __name__ == "__main__":
    main()
