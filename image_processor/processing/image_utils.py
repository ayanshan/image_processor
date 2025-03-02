import requests
from PIL import Image
from io import BytesIO
import os

def compress_image(image_url, output_path):
    """Downloads, compresses, and saves an image."""
    response = requests.get(image_url, stream=True)
    response.raise_for_status()

    img = Image.open(BytesIO(response.content))
    img.save(output_path, "JPEG", quality=50)  # ✅ Compress by 50%
    return output_path

