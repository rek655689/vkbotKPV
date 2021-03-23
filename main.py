import vk_api
import yaml
import requests
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

with open('settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)

session = requests.Session()
token, confirmation_token = settings['token'], settings['confirmation_token']
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session, wait=25)
vk = vk_session.get_api()
key, server, ts = vk.groups.getLongPollServer(group_id=169574362)

while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.text == 'тык':
                vk.messages.send(key=key, server=server, ts=ts, random_id = get_random_id(), user_id=event.user_id, message='робит')