from hashlib import sha1
import mysql.connector


def encode_id(vk_id: str, salt: str) -> str:
    """Кодирование id для идентификации игрока, запросившего настройки"""
    return str(sha1(salt.encode() + vk_id.encode()).hexdigest()[:-2])


def checking_position(bot, vk_id: str) -> None or [str, int]:
    """Проверка игрока на наличие должности в группе, т.е. определение прав доступа"""
    if int(vk_id) not in bot.get_managers(['creator', 'administrator', 'moderator']):
        return 'К сожалению, доступ закрыт', 403


def handler(bot, data) -> str or [str, int]:
    if data["h"] != encode_id(data["vk_id"], bot.salt):
        return 'Для доступа к редактированию напоминаний, пожалуйста, запросите ссылку в боте по команде "настройки"', 403

    match data['type']:
        case 'showNow':
            return showNow(bot, data)
        case 'update':
            return update(bot, data)
        case 'showAv':
            return showAv(bot, data)
        case 'add':
            return add(bot, data)
        case 'add_unique':
            return add_unique(bot, data)
        case 'update_unique':
            return update_unique(bot, data)
        case 'deleteBadId':
            checking_position(bot, data["vk_id"])
            return del_bad_id(bot, data)
        case 'addBadId':
            checking_position(bot, data["vk_id"])
            return add_bad_id(bot, data)
        case 'showAdmin':
            checking_position(bot, data["vk_id"])
            return showAdmin(bot, data)
        case 'delTime':
            checking_position(bot, data["vk_id"])
            return delTime(bot, data)


def get_reminders(bot, vk_id: str = None):
    rows = []
    actions = set()
    if vk_id:
        result = bot.db.get_all('reminders', 'vk_id', vk_id, 'id_schedule')
    else:
        result = bot.db.get_all('reminders', column='id_schedule')

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
    html += f'</table><button type="button" class="btn btn-outline-dark btn-sm" name="hide" data-category="now">скрыть</button>'

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
        bot.db.delete('reminders', 'vk_id', vk_id, extra=f" AND id_schedule='{x}'")
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
    html += f'</table><button type="button" class="btn btn-outline-dark btn-sm" name="hide" data-category="av">скрыть</button>'
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
        bot.db.delete_two('reminders_unique', 'vk_id', vk_id, extra=f" AND id_unique='{x}'")
    return 'ok'


def get_bad_ids(bot):
    """Получение списка ID игроков, которых запрещено принимать в группу"""
    return [x[0] for x in bot.db.get_all('bad_ids', column='bad_id')]


def del_bad_id(bot, data):
    """Удаление игрока из списка запрещённых"""
    bot.db.delete('bad_ids', 'bad_id', data["bad_id"])
    return 'ok'


def add_bad_id(bot, data):
    """Добавление игрока в список запрещённых"""
    try:
        bot.db.add_row('bad_ids', ['bad_id'], [data["bad_id"]])
    except mysql.connector.Error as e:
        if e.errno == 1062:
            return 'Такой ID уже добавлен', 500

    html = f'''<div class="bad_id">{data["bad_id"]} 
            <button type="button" class="btn btn-danger btn-sm del" name="del_bad_id">x</button></div>'''
    return html


def showAdmin(bot, data):
    id_action = data["id_action"]
    html = f'<table class="table table-borderless table-sm">fortime'

    schedule = bot.db_actions.get_all('schedule', 'id_action', id_action, 'id_schedule, day, event_time')

    days = {'ПН': 0, 'ВТ': 1, 'СР': 2, 'ЧТ': 3, 'ПТ': 4, 'СБ': 5, 'ВС': 6}
    schedule = sorted(schedule, key=lambda y: int(y[2][:2]))  # сортировка по времени
    schedule = sorted(schedule, key=lambda x: days.__getitem__(x[1]))  # сортировка по дню недели

    day = ''

    for x in schedule:
        if day != x[1]:
            day = x[1]
            html = html.replace('fortime', '')
            html += f'<tr><td>{day}:</td>fortime<td><input type="text" class="change_time" placeholder="00:00"></td></tr>'

        html = html.replace('fortime', f'<td><input type="text" class="change_time" value="{x[2]}"> <button '
                                       f'type="button" class="btn btn-danger btn-sm del" name="del_time">x</button>'
                                       f'</td>fortime')

    html = html.replace('fortime', '')
    html += f'</table><button type="button" class="btn btn-outline-dark btn-sm" name="hide" data-category="now">скрыть</button>'

    return html


def delTime(bot, data):
    bot.db_actions.delete('schedule', 'id_action', data["id_action"], extra=f" AND day='{data['day']}' AND event_time='{data['time']}'")
    return 'ok'
