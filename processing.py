# -*- coding: utf-8 -*-

import logging

import cv2
import numpy
from PIL import Image

from facealign import detect_faces


# Logging.
logging.basicConfig(format='[%(asctime)s] - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def resize_image(image):
    """Makes sure image dimensions are divisible by 16 and not too big."""
    np_image = numpy.array(image)

    new_y = np_image.shape[0] - np_image.shape[0] % 16
    new_x = np_image.shape[1] - np_image.shape[1] % 16

    if new_x != np_image.shape[0] or new_y != np_image.shape[1]:
        logger.info(f"resizing image to ({new_x}, {new_y})")

        resized_image = cv2.resize(np_image, (new_x, new_y), interpolation=cv2.INTER_AREA)

        return Image.fromarray(resized_image.astype('uint8'), 'RGB')

    return image


def convert_webp_to_jpg(image_filename):
    """Coverts a sticker in webp format to a normal jpg image."""
    logger.info(f"converting webp sticker [{image_filename}] to jpg")

    image = Image.open(image_filename)

    if (image.mode != "RGB"):
        # Remove colors from transparent pixels.
        background = Image.new(image.mode[:-1], image.size, "#fff")
        background.paste(image, image.split()[-1])
        image = background

    new_image_filename = f"{image_filename.rsplit('.', 1)[0]}.jpg"

    image = image.convert("RGB")
    image.save(new_image_filename)

    return new_image_filename


def generate_cropped_images(image, cropping_percent):
    """Generates cropped parts of the animation."""
    logger.info(f"generating cropped images")

    print(image.size)
    width, height = image.size
    crop_size = width * (cropping_percent / 100)
    image_lcrop = image.crop((crop_size, 0, width, height))
    image_rcrop = image.crop((0, 0, width - crop_size, height))

    return [image_lcrop, image_rcrop]


def generate_animation(image_list, intensity, duration, fps):
    """Generates the frames for some seconds of intensification."""
    logger.info(f"generating animation")

    multiply_images = [y for x in image_list for y in (x,) * intensity]
    loop_duration = len(multiply_images) / fps
    required_loops = duration / loop_duration

    return multiply_images * int(required_loops)


def generate_stare(image):
    """Finds faces in image and crops one of them to process."""
    logger.info(f"extracting stare")

    faces = detect_faces(numpy.array(image))

    if len(faces) == 0:
        return image

    return image[faces[0][2]:faces[0][4], faces[0][1]:faces[0][3]]
