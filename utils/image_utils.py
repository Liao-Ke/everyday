import os
import uuid

import requests

_IMAGE_CACHE: dict[str, str] = {}


def download_image(url, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    response = requests.get(url)
    response.raise_for_status()

    unique_file_name = f"{uuid.uuid4().hex}.jpg"
    file_path = os.path.join(save_dir, unique_file_name)

    with open(file_path, "wb") as file:
        file.write(response.content)

    return file_path


def cached_download(url: str, save_dir: str = "./story/images/") -> str | None:
    if url in _IMAGE_CACHE:
        return _IMAGE_CACHE[url]
    path = download_image(url, save_dir)
    if path:
        _IMAGE_CACHE[url] = path
    return path
