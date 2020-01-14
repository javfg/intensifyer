# -*- coding: utf-8 -*-

from datetime import datetime
import logging

import imageio
import numpy
import shutil

from utils import get_todays_path


# Logging.
logging.basicConfig(format='[%(asctime)s] - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def get_image(image, context, format):
    """Gets image from user to bot and saves a copy."""
    now = datetime.now()
    file_id = image['file_id']
    image_subdir = get_todays_path(now)
    image_filename = f"{image_subdir}/{now.strftime('%H-%M-%S')}-{file_id}.{format}"
    image = context.bot.get_file(file_id)

    logger.info(f"downloading image [{image['file_path']}] to [{image_filename}]")

    image.download(image_filename)

    return image_filename


def copy_image(origin, destination):
    """Copy image to another file."""
    shutil.copyfile(origin, destination)


def save_mp4(image_list, video_filename, fps):
    """Generates a mp4 animation with imageio."""
    logger.info(f"saving mp4 [{video_filename}]")

    mp4_writer = imageio.get_writer(video_filename, fps=fps)

    for image in image_list:
        mp4_writer.append_data(numpy.array(image))


def send_video(video_filename, update, context):
    """Sends video from bot to user."""
    username = update.message.from_user.username
    logger.info(f"sending result to [{username}]")

    video_file = open(video_filename, "rb")

    context.bot.send_video(chat_id=update.message.chat_id, video=video_file, supports_streaming=True)
