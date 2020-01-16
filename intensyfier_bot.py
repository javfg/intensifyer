#! /usr/bin/env python3.7
# -*- coding: utf-8 -*-

import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from commands import start, print_help, set_stare, set_zoomstare
from pipeline import take_photo, take_sticker


# Logging.
logging.basicConfig(format='[%(asctime)s] - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Help messages.
help_msgs = ["Here is the *help*!", "Send me a *photo* and I will intensify it."]
help_msgs.append("If you send a *caption* with the photo. You do not need to add the word _intensifies_, I will add it for you!")
help_msgs.append("If you use /stare and then send me a photo, I will look for a *face* in it and intensify the stare.")

# Context: user list.
CallbackContext.chat_data = {'help_msgs': help_msgs}

# Register bot.
with open("secrets") as secret_store:
    telegram_token = secret_store.readline()

updater = Updater(telegram_token, use_context=True)

# Adds command handlers.
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("help", print_help))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, take_photo))
updater.dispatcher.add_handler(MessageHandler(Filters.sticker, take_sticker))
updater.dispatcher.add_handler(CommandHandler("stare", set_stare))
updater.dispatcher.add_handler(CommandHandler("zoomstare", set_zoomstare))

# Start loop.
updater.start_polling()
logger.info("intensyfier bot started")
updater.idle()
