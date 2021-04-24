import vk_api
import yaml
import requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import handler

with open('/settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)

session = requests.Session()
token, confirmation_token, group_id = settings['token'], settings['confirmation_token'], settings['group_id']
vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, group_id, wait=25)
vk = vk_session.get_api()
LongPollServer = vk.groups.getLongPollServer(group_id=group_id)
key, server, ts = LongPollServer['key'], LongPollServer['server'], LongPollServer['ts']

config = {'key': key, 'server': server, 'ts': ts}

while True:
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            handler.answer(vk, settings, config, event.object)
            continue
