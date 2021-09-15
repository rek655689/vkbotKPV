from settings import *


def connect (vk_api, requests, time, local_time):
    VkBotLongPoll = vk_api.bot_longpoll.VkBotLongPoll

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
                        f.write('\nMain: '+local_time+" лонгпул сбросил соединение: "+str(e)+'\n')

    vk_session = vk_api.VkApi(token=token)
    longpoll = SecureVkLongPoll(vk_session, group_id, wait=25)
    vk = vk_session.get_api()
    LongPollServer = vk.groups.getLongPollServer(group_id=group_id)
    key, server, ts = LongPollServer['key'], LongPollServer['server'], LongPollServer['ts']
    config = {'key': key, 'server': server, 'ts': ts}
    return vk, longpoll, config