import actions
import calendar
import datetime
import schedule
import time
import vk_api
import requests
import connection
import traceback

seconds = time.time()
local_time = time.ctime(seconds)


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


vk, longpoll, config = connection.connect(vk_api, requests, time, local_time)

now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day
f_d_month, q_d_month = calendar.monthrange(year, month)[0], calendar.monthrange(year, month)[1]
ost = 6 - f_d_month
weeks = (q_d_month // 7)
f_d_month = weeks * 7 + 1
last_sunday = f_d_month + ost
if last_sunday > q_d_month:
    last_sunday -= 7

if day == last_sunday:
    print(str(now.day) + ' true')
    schedule.every().day.at('17:55').do(actions.brightest_night.send5, vk, config, actions.brightest_night.times[0], actions.brightest_night)
    schedule.every().day.at('17:50').do(actions.brightest_night.send10, vk, config, actions.brightest_night.times[0], actions.brightest_night)
else:
    print(str(now.day) + ' no')

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

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception:
        with open('errors.txt', 'a') as f:
            f.write('\nTime: '+local_time+'\n'+traceback.format_exc())
        continue
