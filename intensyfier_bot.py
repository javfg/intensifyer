#! /usr/bin/env python3.7
# coding=utf-8

import logging
from pathlib import Path
from datetime import datetime
import numpy
from io import BytesIO

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from PIL import Image
import imageio


CROPPING_PERCENT = 5
INTENSITY = 4


# Logging.
logging.basicConfig(format='[%(asctime)s] - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    """Sends welcome message when /start is issued."""
    username = update.message.from_user.username

    logging.info(f"user [{username}] said hello")

    update.message.reply_text(f"Hello {username}. Send me pics or ask for /help!")


def print_help(update, context):
    """Sends help message when /help is issued."""
    username = update.message.from_user.username

    logging.info(f"user [{username}] asked for help")

    update.message.reply_text("For now, you can send me a pic of something you want to itensify.")


def get_todays_path(now):
    """Gets the path for today's images, creating it if it does not exist."""
    todays_path = f"./images/{now.strftime('%Y%m%d')}"

    Path(todays_path).mkdir(parents=True, exist_ok=True)

    return todays_path


def get_image(file_id, context):
    """Gets image from user to bot and saves a copy."""
    image = context.bot.get_file(file_id)
    now = datetime.now()
    image_subdir = get_todays_path(now)
    image_filename = f"{image_subdir}/{now.strftime('%H-%M-%S')}-{file_id}.jpg"

    logging.info(f"downloading image [{image['file_path']}] to [{image_filename}]")

    image.download(image_filename)

    return image_filename


def send_result(intensyfied_filename, update, context):
    """Sends image from bot to user."""
    username = update.message.from_user.username

    logging.info(f"sending result to [{username}]")

    intensyfied_video = open(intensyfied_filename, "rb")

    context.bot.send_video(chat_id=update.message.chat_id, video=intensyfied_video, supports_streaming=True)


def generate_crop_images(image_filename, cropping_percent):
    """Generates cropped parts of the animation."""
    logging.info(f"generating crops for [{image_filename}]")

    image = Image.open(image_filename)
    width, height = image.size
    crop_size = width * (cropping_percent / 100)
    image_lcrop = image.crop((crop_size, 0, width, height))
    image_rcrop = image.crop((0, 0, width - crop_size, height))

    return [image_lcrop, image_rcrop]


def generate_mp4(image_list, image_filename):
    """Generates a mp4 animation with imageio."""
    logging.info(f"generating mp4 for [{image_filename}]")

    intensyfied_filename = f"{image_filename}.mp4"
    mp4_writer = imageio.get_writer(intensyfied_filename, fps=60)
    multiply_images = [y for x in image_list for y in (x,) * INTENSITY]

    for loop in range(0, 10):
        for image in multiply_images:
            mp4_writer.append_data(numpy.array(image))

    mp4_writer.close()

    return intensyfied_filename



def process_image(update, context):
    """Main task. Get image, cut some pixels from each side, create a gif and send back."""
    username = update.message.from_user.username
    logging.info(f"[{username}] sent an image")

    file_id = update.message.photo[-1].file_id

    image_filename = get_image(file_id, context)
    cropped_images = generate_crop_images(image_filename, CROPPING_PERCENT)
    intensyfied_filename = generate_mp4(cropped_images, image_filename.rsplit('.', 1)[0])
    send_result(intensyfied_filename, update, context)


# Register bot.
updater = Updater('948464760:AAEYE6Tzl55jD1KrpRI6LaSBjRfNoibnq_k', use_context=True)

# Adds command handlers
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', print_help))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, process_image))

updater.start_polling()

logging.info("intensyfier bot started")

updater.idle()
