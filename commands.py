# -*- coding: utf-8 -*-

import logging

from telegram import ParseMode

# Logging.
logging.basicConfig(format='[%(asctime)s] - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


#
# Info commands.
#
def start(update, context):
    """Sends welcome message when /start is issued."""
    username = update.message.from_user.username
    logger.info(f"user [{username}] said hello")

    update.message.reply_text(f"Hello {username}. Send me pics or ask for /help!")


def print_help(update, context):
    """Sends help message when /help is issued."""
    username = update.message.from_user.username
    logger.info(f"user [{username}] asked for help")

    for help_msg in context.chat_data['help_msgs']:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=help_msg,
                                 parse_mode=ParseMode.MARKDOWN)


#
# Settings commands.
#
def set_stare(update, context):
    """Sets user config so next image will be a stare image."""
    username = update.message.from_user.username
    logger.info(f"user [{username}] is requesting a stare")

    update.message.reply_text(f"Great! Send me a photo and I will try to find somebody in it.")

    context.user_data['command'] = 'stare'

    print(context.user_data)


#
# Action commands.
#
