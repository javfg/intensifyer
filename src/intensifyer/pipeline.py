import os

from loguru import logger
from PIL import Image
from telegram import Update
from telegram.ext import ContextTypes

import intensifyer.config as config

from .iostuff import copy_image, get_image, save_mp4, send_video
from .processing import (
    caption_images,
    convert_webp_to_jpg,
    fixsize_image,
    generate_animation,
    generate_cropped_images,
    generate_stare,
    resize_image,
)
from .utils import check_image_restrictions, check_sticker_restrictions, user_data


async def take_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Photo processing. Download photo and send to pipeline."""
    user_str = user_data(update)
    logger.info(f"[{user_str}] sent a photo")

    if check_image_restrictions(update):
        image_filename = await get_image(update.message.photo[-1], context, "jpg", user_str)
        caption = update.message.caption or ""
        await pipe(image_filename, update, context, caption)


async def take_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sticker processing. Download sticker and send to pipeline."""
    user_str = user_data(update)
    logger.info(f"[{user_str}] sent a sticker")

    if check_sticker_restrictions(update):
        sticker_filename = await get_image(update.message.sticker, context, "webp", user_str)
        caption = update.message.caption or ""
        await pipe(sticker_filename, update, context, caption, type="sticker")


async def pipe(image_filename, update, context, caption, type="image"):
    command = context.user_data.get("command", "image")
    user_str = user_data(update)
    logger.info(f"[{user_str}] issued [{command}] with caption [{caption}] on type [{type}]")

    image_filename_split = os.path.splitext(image_filename)

    if type == "image":
        image = Image.open(image_filename)
    # This should be removed.
    elif type == "sticker":
        image = Image.open(convert_webp_to_jpg(image_filename))

    if command == "stare":
        copy_image(image_filename, f"{image_filename_split[0]}-full{image_filename_split[1]}")
        image = generate_stare(image)
        context.user_data.pop("command")

    cropped_images = [
        fixsize_image(image) for image in generate_cropped_images(resize_image(image), config.CROPPING_PERCENT)
    ]

    final_images = caption_images(cropped_images, caption) if caption != "" else cropped_images

    animation = generate_animation(final_images, config.INTENSITY, 3, config.FPS)
    video_filename = f"{image_filename_split[0]}.mp4"

    # This should be refactored to do something else with stickers.
    if type == "image" or type == "sticker":
        save_mp4(animation, video_filename, config.FPS, user_str)
        await send_video(video_filename, update, context, user_str)
