import shutil
from datetime import datetime

import imageio
import numpy
from loguru import logger
from telegram.ext import ContextTypes

from .utils import get_todays_path


async def get_image(image, context: ContextTypes.DEFAULT_TYPE, format: str, user_str: str):
    """Gets image from user to bot and saves a copy."""
    now = datetime.now()
    file_id = image["file_id"]
    image_subdir = get_todays_path(now)
    image_filename = f"{image_subdir}/{now.strftime('%H-%M-%S')}-{file_id}.{format}"
    image = await context.bot.get_file(file_id)

    logger.info(f"[{user_str}] fetching image [{image['file_path']}] to [{image_filename}]")

    await image.download_to_drive(image_filename)

    return image_filename


def copy_image(origin, destination):
    """Copy image to another file."""
    shutil.copyfile(origin, destination)


def save_mp4(image_list, video_filename, fps, user_str):
    """Generates a mp4 animation with imageio."""
    logger.info(f"[{user_str}] saving mp4 [{video_filename}]")

    mp4_writer = imageio.get_writer(video_filename, fps=fps)

    for image in image_list:
        mp4_writer.append_data(numpy.array(image))


async def send_video(video_filename, update, context, user_str):
    """Sends video from bot to user."""
    logger.info(f"[{user_str}] sending video [{video_filename}]")

    video_file = open(video_filename, "rb")

    await context.bot.send_animation(chat_id=update.message.chat_id, animation=video_file)
