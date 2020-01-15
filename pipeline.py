# -*- coding: utf-8 -*-

import logging

from PIL import Image
from telegram import ParseMode

import config
from iostuff import get_image, copy_image, save_mp4, send_video
from processing import (
    caption_images,
    convert_webp_to_jpg,
    generate_stare,
    generate_cropped_images,
    generate_animation,
    resize_image,
    fix_size_image,
)
from utils import check_restrictions


# Logging.
logging.basicConfig(format='[%(asctime)s] - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def take_photo(update, context):
    """Photo processing. Download photo and send to pipeline."""
    username = update.message.from_user.username
    logger.info(f"user [{username}] sent a photo")

    image = update.message.photo[-1]

    valid = check_restrictions(image)

    if not valid:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="That photo is *too big*!",
                                 parse_mode=ParseMode.MARKDOWN)
        return

    image_filename = get_image(image, context, "jpg")
    caption = update.message.caption or ""

    pipe(image_filename, update, context, caption)


def take_sticker(update, context):
    """Sticker processing. Download sticker and send to pipeline."""
    username = update.message.from_user.username
    logger.info(f"user [{username}] sent a sticker")

    if update.message.sticker.is_animated:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="No *animated* stickers please!",
                                 parse_mode=ParseMode.MARKDOWN)
        return

    sticker_filename = get_image(update.message.sticker, context, "webp")
    image_filename = convert_webp_to_jpg(sticker_filename)
    caption = update.message.caption or ""

    pipe(image_filename, update, context, caption)


def pipe(image_filename, update, context, caption):
    command = context.user_data['command']
    logger.info(f"processing command [{command}] with caption [{caption}]")

    image_filename_no_ext = image_filename.rsplit('.', 1)[0]

    image = Image.open(image_filename)

    if command == "stare":
        copy_image(image_filename, f"{image_filename_no_ext}-full.jpg")
        image = generate_stare(image)
        context.user_data['command'] = "standard"

    cropped_images = [fix_size_image(image) for image in generate_cropped_images(resize_image(image), config.CROPPING_PERCENT)]
    if caption != "":
        caption_images(cropped_images, caption)
    animation = generate_animation(cropped_images, config.INTENSITY, 3, config.FPS)
    video_filename = f"{image_filename_no_ext}.mp4"
    save_mp4(animation, video_filename, config.FPS)
    send_video(video_filename, update, context)
