import vk_api
import yaml, time, requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import handler


with open('settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)
token, confirmation_token, group_id = settings['token'], settings['confirmation_token'], settings['group_id']


class SecureVkLongPoll(VkBotLongPoll):
    """Обработка разрыва соединения от лонгпула"""
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except requests.exceptions.ReadTimeout as e:
                time.sleep(5)
                with open('errors.txt', 'a') as f:
                    f.write("Лонгпул сбросил соединение:"+str(e)+'\n')


vk_session = vk_api.VkApi(token=token)
longpoll = SecureVkLongPoll(vk_session, group_id, wait=25)
vk = vk_session.get_api()
LongPollServer = vk.groups.getLongPollServer(group_id=group_id)
key, server, ts = LongPollServer['key'], LongPollServer['server'], LongPollServer['ts']
config = {'key': key, 'server': server, 'ts': ts}

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
                handler.answer(vk, settings, config, event.object)
                continue
    except Exception as e:
        time.sleep(5)
        with open('errors.txt', 'a') as f:
            f.write(str(e) + '\n')
        continue
