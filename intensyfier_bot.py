#! /usr/bin/env python3.7
# -*- coding: utf-8 -*-

import logging
import shutil
from datetime import datetime
from pathlib import Path

import numpy
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
from PIL import Image
import imageio
import cv2

from facealign import detect_faces


CROPPING_PERCENT = 3
INTENSITY = 3

users = {}
help_msgs = ["Here is the *help*!", "Send me a *photo* and I will intensify it."]


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
    global help_msgs
    username = update.message.from_user.username

    logging.info(f"user [{username}] asked for help")

    for help_msg in help_msgs:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=help_msg,
                                 parse_mode=ParseMode.MARKDOWN)


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


def generate_crop_images(image, cropping_percent):
    """Generates cropped parts of the animation."""
    logging.info(f"generating crops")

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


def generate_stare(image_filename):
    """Finds faces in image and crops one of them to process."""
    logging.info(f"extracting stare from [{image_filename}]")

    image = cv2.imread(image_filename)
    faces = detect_faces(image)

    if len(faces) == 0:
        return

    shutil.copyfile(image_filename, f"{image_filename}-full.jpg")
    cv2.imwrite(image_filename, image[faces[0][2]:faces[0][4], faces[0][1]:faces[0][3]])


def process_image(update, context):
    """Main task. Get image, cut some pixels from each side, create a gif and send back."""
    global users
    username = update.message.from_user.username
    logging.info(f"user [{username}] sent an image")

    file_id = update.message.photo[-1].file_id
    image_filename = get_image(file_id, context)

    print(users)
    if update.effective_user.id in users:
        command = users[update.effective_user.id]

        logging.info(f"user [{username}] has requested [{command}]")

        if command == "stare":
            generate_stare(image_filename)

        del users[update.effective_user.id]

    image = Image.open(image_filename)
    cropped_images = generate_crop_images(image, CROPPING_PERCENT)
    intensyfied_filename = generate_mp4(cropped_images, image_filename.rsplit('.', 1)[0])
    send_result(intensyfied_filename, update, context)


def set_stare(update, context):
    """Sets user config so next image will be a stare image."""
    global users
    username = update.message.from_user.username
    logging.info(f"user [{username}] is requesting a stare")

    update.message.reply_text(f"Great! Send me a photo and I will try to find somebody in it.")

    users[update.effective_user.id] = 'stare'


# Extra command helps.
help_msgs.append("If you use /stare and then send me a photo, I will look for a *face* in it and intensify the stare.")

# Register bot.
with open("secrets") as secret_store:
    telegram_token = secret_store.readline()

updater = Updater(telegram_token, use_context=True)

# Adds command handlers
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("help", print_help))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, process_image))
updater.dispatcher.add_handler(CommandHandler("stare", set_stare))

updater.start_polling()

logging.info("intensyfier bot started")

updater.idle()
