# -*- coding: utf-8 -*-

from pathlib import Path

from loguru import logger
from telegram.constants import ParseMode

import intensifyer.config as config


def get_todays_path(now):
    """Gets the path for today's images, creating it if it does not exist."""
    todays_path = f"./images/{now.strftime('%Y%m%d')}"

    Path(todays_path).mkdir(parents=True, exist_ok=True)

    return todays_path


def check_image_restrictions(update):
    """Check dimensions and file size of the image are not too big."""
    image = update.message.photo[-1]
    logger.info(
        f"[{user_data(update)}] checking image {image.file_id}" + f"({image.width}x{image.height}, {image.file_size})"
    )

    if image.width > config.MAX_WIDTH or image.height > config.MAX_HEIGHT or image.file_size > config.MAX_FILE_SIZE:
        update.message.reply_text(
            chat_id=update.message.chat_id, text="That photo is *too big*!", parse_mode=ParseMode.MARKDOWN
        )
        return False
    return True


def check_sticker_restrictions(update):
    """Check sticker is not animated."""
    sticker = update.message.sticker
    logger.info(
        f"[{user_data(update)}] checking sticker {sticker.file_id}"
        + f"({sticker.width}x{sticker.height}, {sticker.file_size})"
    )

    if sticker.is_animated:
        update.message.reply_text(
            chat_id=update.message.chat_id, text="No *animated* stickers please!", parse_mode=ParseMode.MARKDOWN
        )
        return False
    return True


def user_data(update):
    """Returns user information string for logging purposes."""
    user_name = update.message.from_user.username
    user_id = update.message.from_user.id

    return f"{user_name} ({user_id})"
