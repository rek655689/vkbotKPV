from hashlib import sha1


def handler(bot, data):
    h = data["h"]
    if h != sha1(bot.salt.encode() + data["vk_id"].encode()).hexdigest()[:-2]:
        return 'Для доступа к редактированию напоминаний, пожалуйста, запросите ссылку в боте по команде "настройки"'

    match data['type']:
        case 'showNow':
            showNow(bot, data)
        case 'update':
            update(bot, data)
        case 'showAv':
            showAv(bot, data)
        case 'add':
            add(bot, data)
        case 'add_unique':
            add_unique(bot, data)
        case'update_unique':
            update_unique(bot, data)


def get_reminders(bot, vk_id):
    rows = []
    actions = set()
    result = bot.db.get_all('reminders', 'vk_id', vk_id, 'id_schedule')

    for id_schedule in [m[0] for m in result]:
        actions.add(bot.db_actions.get_one('schedule', 'id_schedule', id_schedule, 'id_action')[0])

    for id_action in actions:
        title = bot.db_actions.get_one('listing', 'id_action', id_action, 'title')[0]
        rows.append([id_action, title])

    return rows


def showNow(bot, data):
    id_action = data["id_action"]
    vk_id = data["vk_id"]
    html = f'<table class="table table-borderless table-sm">fortime'

    now = bot.db.get_all('reminders', column='reminders.id_schedule, reminders.remind_time',
                         extra=f" LEFT JOIN actions.schedule ON reminders.id_schedule = schedule.id_schedule AND "
                               f"reminders.vk_id = '{vk_id}' WHERE schedule.id_action = '{id_action}'")
    now = {str(m[0]): m[1] for m in now}

    schedule = bot.db_actions.get_all('schedule', column='id_schedule, day, event_time',
                                      extra=f" WHERE id_schedule IN ({' ,'.join(now.keys())})")

    days = {'ПН': 0, 'ВТ': 1, 'СР': 2, 'ЧТ': 3, 'ПТ': 4, 'СБ': 5, 'ВС': 6}
    schedule = sorted(schedule, key=lambda y: int(y[2][:2]))  # сортировка по времени
    schedule = sorted(schedule, key=lambda x: days.__getitem__(x[1]))  # сортировка по дню недели

    day = ''

    for x in schedule:
        if day != x[1]:
            day = x[1]
            html = html.replace('fortime', '')
            html += f'<tr><td>{day}:</td>fortime</tr>'

        html = html.replace('fortime', f'<td><div name="sch_select"><input class="form-check-input" '
                                       f'type="checkbox" style="margin-right: 5px;" value="sch{x[0]}" id="sch{x[0]}" '
                                       f'name="sch_time"><label class="form-check-label" for="sch{x[0]}">'
                                       f'{x[2]}</label>fortime')
        if now.get(str(x[0])) == '5':
            html = html.replace('fortime', '<select class="form-select form-select-sm" style="margin-left: 3px;">'
                                           '<option value="5">5</option><option value="10">10</option></select>'
                                           '</td>fortime')
        else:
            html = html.replace('fortime', '<select class="form-select form-select-sm" style="margin-left: 3px;">'
                                           '<option value="10">10</option><option value="5">5</option></select>'
                                           '</td>fortime')

    html = html.replace('fortime', '')
    html += f'</table><button type="button" class="btn btn-outline-dark btn-sm" name="btn_hide" data-category="now">скрыть</button>'

    return html


def get_actions(bot) -> list:
    rows = []

    for x in bot.db_actions.get_all('listing'):
        id_action, title = x[0], x[1]
        rows.append([id_action, title])

    return rows


def update(bot, data):
    vk_id = data['vk_id']
    for_del = data['for_del']
    change_time = dict(sorted(data['change_time'], key=lambda x: int(x[0])))

    now_time = bot.db.get_all('reminders', 'vk_id', vk_id, 'id, id_schedule, remind_time',
                              extra=f" AND id_schedule IN ({', '.join(change_time.keys())})")
    now_time = sorted(now_time, key=lambda x: int(x[1]))

    for x in now_time:
        if change_time.get(str(x[1])) != x[2]:
            bot.db.upd('reminders', 'id', x[0], 'remind_time', change_time.get(str(x[1])))

    for x in for_del:
        bot.db.delete_two('reminders', 'vk_id', vk_id, 'id_schedule', x)
    return 'ok'


def showAv(bot, data):
    id_action = data["id_action"]
    html = f'<table class="table table-borderless table-sm">fortime'

    schedule = bot.db_actions.get_all('schedule', 'id_action', id_action, 'id_schedule, day, event_time')
    now = bot.db.get_all('reminders', 'vk_id', data["vk_id"], 'id_schedule')
    now = [m[0] for m in now]

    days = {'ПН': 0, 'ВТ': 1, 'СР': 2, 'ЧТ': 3, 'ПТ': 4, 'СБ': 5, 'ВС': 6}
    schedule = sorted(schedule, key=lambda y: int(y[2][:2]))  # сортировка по времени
    schedule = sorted(schedule, key=lambda x: days.__getitem__(x[1]))  # сортировка по дню недели

    day = ''

    for x in schedule:
        if day != x[1]:
            day = x[1]
            html = html.replace('fortime', '')
            html += f'<tr><td>{day}:</td>fortime</tr>'

        html = html.replace('fortime', f'<td><div name="sch_select"><input class="form-check-input" '
                                       f'type="checkbox" style="margin-right: 5px;" value="sch{x[0]}" id="sch{x[0]}" '
                                       f'%><label class="form-check-label" '
                                       f'for="sch{x[0]}">{x[2]}</label>fortime')
        if x[0] in now:
            html = html.replace('%', ' checked disabled')
        else:
            html = html.replace('%', '')
            html = html.replace('fortime', '<select class="form-select form-select-sm" style="margin-left: 3px;" '
                                           'name="sch_rtime"><option value="5">5</option><option value="10">10</option>'
                                           '</select></div></td>fortime')

    html = html.replace('fortime', '')
    html += f'</table><button type="button" class="btn btn-outline-dark btn-sm" name="btn_hide" data-category="av">скрыть</button>'
    return html


def add(bot, data):
    add_actions = data['add_actions']
    for x in add_actions:
        bot.db.add_row('reminders', ['vk_id', 'id_schedule', 'remind_time'], [data["vk_id"], x[0], x[1]])
    return 'ok'


def get_unique_now(bot, vk_id):
    rows = []
    result = bot.db.get_all('reminders_unique', 'vk_id', vk_id)

    for x in result:
        u = bot.db_actions.get_one('listing_unique', 'id_unique', x[2])
        rows.append([x[2], u[1], u[2], x[3]])
    return rows


def get_unique_available(bot, vk_id):
    rows = []

    for x in bot.db_actions.get_all('listing_unique'):
        if bot.db.get_one('reminders_unique', 'vk_id', vk_id, extra=f' AND id_unique="{x[0]}"'):
            rows.append([*x, True])
        else:
            rows.append([*x, False])
    return rows


def add_unique(bot, data):
    add = data['add']
    for x in add:
        bot.db.add_row('reminders_unique', ['vk_id', 'id_unique', 'remind_time'], [data["vk_id"], x[0], x[1]])
    return 'ok'


def update_unique(bot, data):
    vk_id = data['vk_id']
    for_del = data['for_del']
    change_time = dict(sorted(data['change_time'], key=lambda x: int(x[0])))

    now_time = bot.db.get_all('reminders_unique', 'vk_id', vk_id, 'id, id_unique, remind_time')
    now_time = sorted(now_time, key=lambda x: int(x[1]))

    for x in now_time:
        if change_time.get(str(x[1])) != x[2]:
            bot.db.upd('reminders_unique', 'id', x[0], 'remind_time', change_time.get(str(x[1])))

    for x in for_del:
        bot.db.delete_two('reminders_unique', 'vk_id', vk_id, 'id_unique', x)
    return 'ok'
