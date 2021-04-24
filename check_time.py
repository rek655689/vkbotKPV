import time, schedule, vk_api, yaml, actions
from vk_api.bot_longpoll import VkBotLongPoll

with open('/settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)

token, confirmation_token, group_id = settings['token'], settings['confirmation_token'], settings['group_id']
vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, group_id, wait=25)
vk = vk_session.get_api()
LongPollServer = vk.groups.getLongPollServer(group_id=group_id)
key, server, ts = LongPollServer['key'], LongPollServer['server'], LongPollServer['ts']

config = {'key': key, 'server': server, 'ts': ts}


def minutes(t):
    t = t.split(":")
    h1 = int((t[0])[0])
    h2 = int((t[0])[1])
    min1 = int((t[1])[0])
    min2 = int((t[1])[1])

    min1 = min1 - 1
    if min1 < 0:
        min1 = 5
        h2 = h2 - 1
        if h2 < 0:
            h2 = 9
            h1 = h1 - 1

    t = f'{h1}{h2}:{min1}{min2}'
    return t


for action in actions.action_list:
    name = action.get_var_name()
    for times in action.times:
        schedule.every().day.at(minutes(times)).do((eval('actions.' + name + '.send')), vk, config, times)

while True:
    schedule.run_pending()
    time.sleep(1)
