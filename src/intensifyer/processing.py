import cv2
import numpy
from loguru import logger
from PIL import Image, ImageDraw, ImageFont

import intensifyer.config as config

from .facealign import detect_faces


def fixsize_image(image):
    """Makes sure image dimensions divisible by 16."""
    np_image = numpy.array(image)

    h = np_image.shape[0] - np_image.shape[0] % 16
    w = np_image.shape[1] - np_image.shape[1] % 16

    if w != np_image.shape[0] or h != np_image.shape[1]:
        logger.debug(f"resizing image to ({w}, {h})")

        resized_image = cv2.resize(np_image, (w, h), interpolation=cv2.INTER_AREA)

        return Image.fromarray(resized_image.astype("uint8"), "RGB")

    return image


def resize_image(image):
    """Makes sure image dimensions are not too big."""
    np_image = numpy.array(image)
    h, w, _ = np_image.shape

    if w > config.OUTPUT_SIZE:
        h = int(h * config.OUTPUT_SIZE / w)
        w = config.OUTPUT_SIZE

    if h > config.OUTPUT_SIZE:
        w = int(w * config.OUTPUT_SIZE / h)
        h = config.OUTPUT_SIZE

    if w != np_image.shape[0] or h != np_image.shape[1]:
        logger.debug(f"resizing image to ({w}, {h})")

        resized_image = cv2.resize(np_image, (w, h), interpolation=cv2.INTER_AREA)

        return Image.fromarray(resized_image.astype("uint8"), "RGB")

    return image


def sticker_resize(image):
    """Makes sure output image is 512x512."""
    np_image = numpy.array(image)

    return cv2.resize(np_image, (512, 512), interpolation=cv2.INTER_AREA)


def convert_webp_to_jpg(image_filename):
    """Coverts a sticker in webp format to a normal jpg image."""
    logger.info(f"converting webp sticker [{image_filename}] to jpg")

    image = Image.open(image_filename)

    if image.mode != "RGB":
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
    width, height = image.size
    cropsize_multiplier = config.OUTPUT_SIZE / min([width, height])
    crop_size = int(min([width, height]) * (cropping_percent / 100) * cropsize_multiplier)
    logger.info(f"generating cropped images (crop size [{crop_size} px])")

    image_lt_crop = image.crop((crop_size, crop_size, width, height))
    image_lb_crop = image.crop((crop_size, 0, width, height - crop_size))
    image_rt_crop = image.crop((0, crop_size, width - crop_size, height))
    image_rb_crop = image.crop((0, 0, width - crop_size, height - crop_size))

    return [image_lt_crop, image_lb_crop, image_rt_crop, image_rb_crop]


def generate_animation(image_list, intensity, duration, fps):
    """Generates the frames for some seconds of intensification."""
    logger.info("generating animation")

    multiply_images = [y for x in image_list for y in (x,) * intensity]
    loop_duration = len(multiply_images) / fps
    required_loops = duration / loop_duration

    return multiply_images * int(required_loops)


def generate_stare(image):
    """Finds faces in image and crops one of them to process."""
    logger.info("extracting stare")

    np_image = numpy.array(image)
    np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)

    faces = detect_faces(np_image)

    if len(faces) == 0:
        return image

    face_np_image = cv2.cvtColor(np_image[faces[0][2] : faces[0][4], faces[0][1] : faces[0][3]], cv2.COLOR_BGR2RGB)
    face_image = Image.fromarray(face_np_image.astype("uint8"), "RGB")

    return face_image


def caption_images(image_list, caption):
    """Captions an image. For now, lets assume order is LT, LB, RT, RB."""
    logger.info(f"captioning [{caption}] into images")

    caption = f"{caption[:32].upper()}\nINTENSIFIES"

    for image in image_list:
        font_size = int(max(image.size) / 16)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("resources/impact.ttf", size=font_size)

        # Get text dimensions
        bbox = draw.multiline_textbbox((0, 0), caption, font=font, align="center")
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position
        x = (image.size[0] - text_width) / 2
        y = image.size[1] - text_height - (image.size[1] * 0.05)  # 5% padding from bottom

        draw.multiline_text(
            xy=(x, y),
            text=caption,
            fill=(255, 255, 255),
            font=font,
            align="center",
            stroke_width=3,
            stroke_fill=(31, 31, 31),
        )

    return image_list
