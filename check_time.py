import time, schedule, vk_api, yaml, actions
from vk_api.bot_longpoll import VkBotLongPoll

with open('settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)

token, confirmation_token, group_id= settings['token'], settings['confirmation_token'], settings['group_id']
vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, group_id, wait=25)
vk = vk_session.get_api()
LongPollServer = vk.groups.getLongPollServer(group_id=group_id)
key, server, ts = LongPollServer['key'], LongPollServer['server'], LongPollServer['ts']

config = {'key': key, 'server': server, 'ts': ts}


for action in actions.action_list:
    name = action.get_var_name()
    for t in action.times:
        schedule.every().day.at(t).do((eval('actions.'+name+'.send')), vk, config, str(t))

while True:
    schedule.run_pending()
    time.sleep(1)