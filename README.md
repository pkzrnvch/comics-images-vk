# XKCD comics to VK

This program fetches random XKCD comic and publishes it to vk.com community.

### How to install

Create an `.env` file in the project directory. Get your vk.com community ID and assign it to `VK_GROUP_ID` environment variable. To create posts through a vk.com API you will need an access token. First, create an app at [vk.com developers page](https://vk.com/dev), its type should be set to `standalone`. After that, refer [here](https://vk.com/dev/implicit_flow_user) for further instructions. You will need the following access rights: `photos`, `groups`, `wall` and `offline`, `redirect_uri` parameter should be omitted. As a result, you will get your access token, it will be shown in the address bar. Assign it to `VK_ACCESS_TOKEN` environment variable. 

Example of an `.env` file:

```
VK_ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
VK_GROUP_ID = 'YOURG_GROUP_ID'
```

Python3 should already be installed. Use pip (or pip3, in case of conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

### Usage

To run the programm use the following command from the project directory:
```
python main.py
```

### Project Goals

The code is written for educational purposes on online-course for web-developers [Devman](https://dvmn.org).
