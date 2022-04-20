import os
import random
from pathlib import Path
from urllib.parse import urlsplit

import requests
from dotenv import load_dotenv


def download_image(image_url, filename, payload=None):
    response = requests.get(image_url, params=payload)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)


def get_filename(image_url):
    split_url = urlsplit(image_url)
    url_path = Path(split_url.path)
    filename = url_path.name
    return filename


def choose_comic_to_post():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    last_comic_number = response.json()['num']
    comic_number = random.randint(1, last_comic_number)
    return comic_number


def get_vk_upload_url(vk_access_token, vk_group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {
        'access_token': vk_access_token,
        'group_id': vk_group_id,
        'v': 5.131,
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    vk_upload_photo_url = response.json()['response']['upload_url']
    return vk_upload_photo_url


def main():
    load_dotenv()
    vk_access_token = os.environ.get('VK_ACCESS_TOKEN')
    vk_group_id = os.environ.get('VK_GROUP_ID')

    comic_number = choose_comic_to_post()
    xkcd_api_url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(xkcd_api_url)
    response.raise_for_status()
    comic_metadata = response.json()
    comic_image_url = comic_metadata['img']
    comic_comment = comic_metadata['alt']
    comic_image_filename = get_filename(comic_image_url)
    download_image(comic_image_url, comic_image_filename)

    vk_upload_url = get_vk_upload_url(vk_access_token, vk_group_id)
    with open(comic_image_filename, 'rb') as file:
        files = {'photo': file}
        vk_upload_response = requests.post(vk_upload_url, files=files)
        vk_upload_response.raise_for_status()
    uploaded_photo = vk_upload_response.json()

    vk_save_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    payload = {
        'access_token': vk_access_token,
        'group_id': vk_group_id,
        'v': 5.131,
        'photo': uploaded_photo['photo'],
        'server': uploaded_photo['server'],
        'hash': uploaded_photo['hash'],
    }
    vk_save_response = requests.get(vk_save_url, params=payload)
    vk_save_response.raise_for_status()
    saved_photo = vk_save_response.json()

    vk_publish_url = 'https://api.vk.com/method/wall.post'
    media_id = saved_photo['response'][0]['id']
    owner_id = saved_photo['response'][0]['owner_id']
    attachments = f'photo{owner_id}_{media_id}'
    payload = {
        'access_token': vk_access_token,
        'owner_id': f'-{vk_group_id}',
        'from_group': 1,
        'attachments': attachments,
        'message': comic_comment,
        'v': 5.131,
    }
    vk_publish_response = requests.post(vk_publish_url, params=payload)
    vk_publish_response.raise_for_status()

    os.remove(comic_image_filename)


if __name__ == '__main__':
    main()
