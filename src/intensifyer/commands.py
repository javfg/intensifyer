from loguru import logger
from telegram import Update
from telegram.ext import CallbackContext

from .utils import user_data

help_msg = (
    "Here is the *help*!\nSend me a *photo* and I will intensify it.\n"
    "If you send a *caption* with the photo. You do not need to add the word _intensifies_, I will add it for you!\n"
    "If you use /stare and then send me a photo, I will look for a *face* in it and intensify the stare."
)


#
# Info commands.
#
async def start(update: Update, context: CallbackContext):
    """Sends welcome message when /start is issued."""
    logger.info(f"[{user_data(update)}] said hello")
    username = update.message.from_user.username
    await update.message.reply_text(f"Hello {username}. Send me pics or ask for /help!")


async def print_help(update: Update, context: CallbackContext):
    """Sends help message when /help is issued."""
    logger.info(f"[{user_data(update)}] asked for help")
    await update.message.reply_markdown(help_msg)


#
# Settings commands.
#
async def set_stare(update: Update, context: CallbackContext):
    """Sets user config so next image will be a stare image."""
    logger.info(f"[{user_data(update)}] requested a stare")
    context.user_data["command"] = "stare"
    await update.message.reply_text("Great! Send me a photo and I will try to find somebody in it.")


async def set_zoomstare(update: Update, context: CallbackContext):
    """Sets user config so next image will be a stare image."""
    logger.info(f"[{user_data(update)}] requested a zoomstare")
    context.user_data["command"] = "zoomstare"
    await update.message.reply_text("Great! Send me a photo and I will try to find somebody in it.")
