import time, schedule, vk_api, yaml, actions
from vk_api.bot_longpoll import VkBotLongPoll
import calendar
import datetime

with open('settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)

token, confirmation_token, group_id = settings['token'], settings['confirmation_token'], settings['group_id']


def l_s():
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    f_d_month, q_d_month = calendar.monthrange(year, month)[0], calendar.monthrange(year, month)[1]
    ost = 6 - f_d_month
    weeks = (q_d_month // 7)
    f_d_month = weeks * 7 + 1
    last_sunday = f_d_month + ost
    if last_sunday > q_d_month:
        last_sunday -= 7

    if now.day == last_sunday:
        schedule.every().day.at('17:55').do(actions.brightest_night.send5, vk, config, times, actions.brightest_night)
        schedule.every().day.at('17:50').do(actions.brightest_night.send10, vk, config, times, actions.brightest_night)
        return schedule.CancelJob


def minutes10(t):
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


def minutes5(t):
    t = t.split(":")
    h1 = int((t[0])[0])
    h2 = int((t[0])[1])
    min1 = int((t[1])[0])
    min2 = int((t[1])[1])

    min1 = min1 - 1
    min2 = 5
    if min1 < 0:
        min1, min2 = 5, 5
        h2 = h2 - 1
        if h2 < 0:
            h2 = 9
            h1 = h1 - 1

    t = f'{h1}{h2}:{min1}{min2}'
    return t


vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, group_id, wait=25)
vk = vk_session.get_api()
LongPollServer = vk.groups.getLongPollServer(group_id=group_id)
key, server, ts = LongPollServer['key'], LongPollServer['server'], LongPollServer['ts']
config = {'key': key, 'server': server, 'ts': ts}

for action in actions.action_list:
    name = action.get_var_name()
    if action not in actions.other_actions:
        for times in action.times:
            schedule.every().day.at(minutes5(times)).do(eval('actions.' + name + '.send5'), vk, config, times, action)
            schedule.every().day.at(minutes10(times)).do(eval('actions.' + name + '.send10'), vk, config, times, action)

for action in actions.other_actions:
    name = action.get_var_name()
    if name == 'meeting':
        times = ['18:00', '18:00', '19:00', '18:00', '18:00', '18:00', '16:00']
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for d, t in zip(days, times):
            eval(
                f"schedule.every().{d}.at('{minutes5(t)}').do(actions.meeting.send5, vk, config, '{t}', actions.meeting)")
            eval(
                f"schedule.every().{d}.at('{minutes10(t)}').do(actions.meeting.send10, vk, config, '{t}', actions.meeting)")

schedule.every().day.at('00:00').do(l_s)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e) + '\n')
        vk_session = vk_api.VkApi(token=token)
        longpoll = VkBotLongPoll(vk_session, group_id, wait=25)
        vk = vk_session.get_api()
        LongPollServer = vk.groups.getLongPollServer(group_id=group_id)
        key, server, ts = LongPollServer['key'], LongPollServer['server'], LongPollServer['ts']
        config = {'key': key, 'server': server, 'ts': ts}
        continue
