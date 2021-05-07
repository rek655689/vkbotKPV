import vk_api
import yaml
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import handler

with open('settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)
token, confirmation_token, group_id = settings['token'], settings['confirmation_token'], settings['group_id']

while True:
    vk_session = vk_api.VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, group_id, wait=25)
    vk = vk_session.get_api()
    LongPollServer = vk.groups.getLongPollServer(group_id=group_id)
    key, server, ts = LongPollServer['key'], LongPollServer['server'], LongPollServer['ts']
    config = {'key': key, 'server': server, 'ts': ts}

    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
                handler.answer(vk, settings, config, event.object)
                continue
    except Exception as e:
        with open('errors.txt', 'a') as f:
           f.write(str(e) + '\n')
        continue
