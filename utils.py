# -*- coding: utf-8 -*-

from pathlib import Path
import logging

import config


# Logging.
logging.basicConfig(format='[%(asctime)s] - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def get_todays_path(now):
    """Gets the path for today's images, creating it if it does not exist."""
    todays_path = f"./images/{now.strftime('%Y%m%d')}"

    Path(todays_path).mkdir(parents=True, exist_ok=True)

    return todays_path


def check_restrictions(image):
    logger.info(f"checking image {image.file_id}, resolution is ({image.width}, {image.height})")

    return (image.width <= config.MAX_WIDTH
            and image.height <= config.MAX_HEIGHT
            and image.file_size <= config.MAX_FILE_SIZE)
