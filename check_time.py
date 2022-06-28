import schedule
import time
from datetime import datetime
import calendar
from user import User


def check_time(bot, group_id):
    days = {'ПН': 'monday', 'ВТ': 'tuesday', 'СР': 'wednesday', 'ЧТ': 'thursday', 'ПТ': 'friday', 'СБ': 'saturday', 'ВС': 'sunday'}

    actions = {x[0]: x[1] for x in bot.db_actions.get_all('listing')}

    for id_action, title in actions.items():
        schd = [[x[0], x[1], x[2]] for x in bot.db_actions.get_all('schedule', 'id_action', id_action, 'id_schedule, day, event_time')]
        for id_schedule, day, event_time in schd:
            day = days.get(day)
            eval(f'schedule.every().{day}.at("{minutes(event_time, 5)}").do(send, bot, group_id, id_schedule, title, "5")')
            eval(f'schedule.every().{day}.at("{minutes(event_time, 10)}").do(send, bot, group_id,  id_schedule, title, "10")')

    now = datetime.now()
    if now.day == last_sunday(now):
        eval(f'schedule.every().day.at("{minutes("18:00", 5)}").do(brightest_night, bot, group_id, "5")')
        eval(f'schedule.every().day.at("{minutes("18:00", 10)}").do(brightest_night, bot, group_id, "10")')


def send(bot, group_id, id_schedule, title, remind_time):
    ids = [x[0] for x in bot.db.get_all('reminders', 'id_schedule', id_schedule, 'vk_id', f" AND remind_time='{remind_time}'")]
    answer = {'message': f'Через {remind_time} минут будет {title}'}
    for vk_id in ids:
        data = {'type': 'message_event', 'object': {'user_id': vk_id}}
        bot.user = User(data, group_id, bot)
        bot.send(answer, False)


def brightest_night(bot, group_id, remind_time):
    ids = [x[0] for x in bot.db.get_all('reminders_unique', 'id_unique', 1, 'vk_id', f" AND remind_time='{remind_time}'")]
    answer = {'message': f'Через {remind_time} минут будет Самая Яркая Ночь'}
    for vk_id in ids:
        data = {'type': 'message_event', 'object': {'user_id': vk_id}}
        bot.user = User(data, group_id, bot)
        bot.send(answer, False)
    return schedule.CancelJob


def minutes(t, x):
    h, m = map(int, t.split(":"))
    m -= x
    if m < 0:
        h -= 1
        m += 60

    if len(str(h)) < 2:
        h = f'0{h}'

    if len(str(m)) < 2:
        m = f'0{m}'

    return f'{h}:{m}'


def last_sunday(now):
    month = calendar.monthcalendar(now.year, now.month)
    sundays = [week[6] for week in month if week[6] > 0]
    return sundays[-1]


def check_time_start(bot, group_id):
    schedule.every().day.do(check_time, bot, group_id)

    while True:
        schedule.run_pending()
        time.sleep(1)