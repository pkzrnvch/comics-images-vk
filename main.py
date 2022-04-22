import os
import random
from pathlib import Path
from urllib.parse import urlsplit

import requests
from dotenv import load_dotenv


class VkApiError(Exception):
    pass


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


def check_vk_response(response):
    response = response.json()
    if 'error' in response:
        raise VkApiError(
            f'Error code {response["error"]["error_code"]} -'
            f' {response["error"]["error_msg"]}'
        )


def choose_comic_to_post():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    last_comic_number = response.json()['num']
    comic_number = random.randint(1, last_comic_number)
    return comic_number


def fetch_comic(comic_number):
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comic_metadata = response.json()
    comic_image_url = comic_metadata['img']
    comic_comment = comic_metadata['alt']
    comic_image_filename = get_filename(comic_image_url)
    download_image(comic_image_url, comic_image_filename)
    return comic_image_filename, comic_comment


def get_vk_upload_url(vk_access_token, vk_group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {
        'access_token': vk_access_token,
        'group_id': vk_group_id,
        'v': 5.131,
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_vk_response(response)
    vk_upload_url = response.json()['response']['upload_url']
    return vk_upload_url


def upload_photo_to_vk(upload_url, filename):
    with open(filename, 'rb') as file:
        files = {'photo': file}
        response = requests.post(upload_url, files=files)
        check_vk_response(response)
        response.raise_for_status()
    uploaded_photo = response.json()
    return uploaded_photo


def save_photo_to_vk(uploaded_photo, vk_access_token, vk_group_id):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    payload = {
        'access_token': vk_access_token,
        'group_id': vk_group_id,
        'v': 5.131,
        'photo': uploaded_photo['photo'],
        'server': uploaded_photo['server'],
        'hash': uploaded_photo['hash'],
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_vk_response(response)
    saved_photo = response.json()
    return saved_photo


def publish_photo_to_vk(photo, comment, vk_access_token, vk_group_id):
    url = 'https://api.vk.com/method/wall.post'
    media_id = photo['response'][0]['id']
    owner_id = photo['response'][0]['owner_id']
    attachments = f'photo{owner_id}_{media_id}'
    payload = {
        'access_token': vk_access_token,
        'owner_id': f'-{vk_group_id}',
        'from_group': 1,
        'attachments': attachments,
        'message': comment,
        'v': 5.131,
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    print(response.json())
    check_vk_response(response)


def main():
    load_dotenv()
    vk_access_token = os.environ.get('VK_ACCESS_TOKEN')
    vk_group_id = os.environ.get('VK_GROUP_ID')
    comic_number = choose_comic_to_post()
    comic_image_filename, comic_comment = fetch_comic(comic_number)
    try:
        upload_url = get_vk_upload_url(vk_access_token, vk_group_id)
        uploaded_photo = upload_photo_to_vk(upload_url, comic_image_filename)
        saved_photo = save_photo_to_vk(
            uploaded_photo,
            vk_access_token,
            vk_group_id
        )
        publish_photo_to_vk(
            saved_photo,
            comic_comment,
            vk_access_token,
            vk_group_id
        )
        print('Comic was successfully published!')
    except VkApiError as error:
        print('Comic was not published - VK API returned the following error: '
              f'{str(error)}')
    finally:
        os.remove(comic_image_filename)


if __name__ == '__main__':
    main()
