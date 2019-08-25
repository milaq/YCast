import logging
import requests
import io

from PIL import Image

import ycast.generic as generic
from ycast import __version__

MAX_SIZE = 290


def get_icon_from_url(iconurl):
    # TODO cache icons on disk
    headers = {'User-Agent': generic.USER_AGENT + '/' + __version__}
    try:
        response = requests.get(iconurl, headers=headers)
    except requests.exceptions.ConnectionError as err:
        logging.error("Connection to station icon URL failed (%s)", err)
        return None
    if response.status_code != 200:
        logging.error("Could not get station icon data from %s (HTML status %s)", iconurl, response.status_code)
        return None
    try:
        image = Image.open(io.BytesIO(response.content))
        image = image.convert("RGB")
        if image.size[0] > image.size[1]:
            ratio = MAX_SIZE / image.size[0]
        else:
            ratio = MAX_SIZE / image.size[1]
        image = image.resize((int(image.size[0] * ratio), int(image.size[1] * ratio)), Image.ANTIALIAS)
        with io.BytesIO() as output_img:
            image.save(output_img, format="JPEG")
            image_conv = output_img.getvalue()
    except Exception as e:
        logging.error("Station icon conversion error (%s)", e)
        return None
    return image_conv
