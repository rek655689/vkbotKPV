from flask import Flask, request, render_template
import json
from threading import Thread

from bot import Bot
from user import User
import site_func
from check_time import check_time_start

# Тестирование
from os import system
system('start /b lt -p 5000 --subdomain vkbotkpv')

# Инициализация приложения, бота, потока для рассылок напоминаний
app = Flask(__name__)
app.config.from_envvar('SETTINGS')
bot = Bot(app.config)
Thread(target=check_time_start, args=(bot, app.config['GROUP_ID']), daemon=True).start()


@app.route('/vk', methods=['POST'])
def processing():
    data = json.loads(request.data)
    if data['type'] == 'confirmation':
        return '8818fecf'
    if data['secret'] != app.config['SECRET_KEY']:
        return 'not vk'
    if data['type'] == 'message_new' or data['type'] == 'message_event':
        bot.user = User(data, app.config['GROUP_ID'], bot)
        bot.handler(data)
    if data['type'] == 'group_leave':
        return 'not ok'  # TODO
    return 'ok'


@app.route('/handler', methods=['GET', 'POST'])
def handler():
    """Обращения к серверу из JS"""
    data = json.loads(request.data)
    response = site_func.handler(bot, data)
    return response


@app.route('/settings', methods=['GET'])
def settings():
    # подтверждение личности игрока
    h = request.args.get('h')
    if h != site_func.encode_id(request.args.get('id'), bot.salt):
        return 'Для доступа к редактированию напоминаний, пожалуйста, запросите ссылку в боте по команде "настройки"'

    reminders = site_func.get_reminders(bot, request.args.get('id'))
    actions = site_func.get_actions(bot)
    unique_now = site_func.get_unique_now(bot, request.args.get('id'))
    unique_available = site_func.get_unique_available(bot, request.args.get('id'))
    return render_template('settings.html', rows_now=reminders, rows_available=actions,
                           rows_unique_now=unique_now, rows_unique_available=unique_available)


@app.route('/admin', methods=['GET'])
def admin():
    if int(request.args.get('id')) not in bot.get_managers(['creator', 'administrator', 'moderator']):
        return 'К сожалению, доступ к странице закрыт'

    h = request.args.get('h')
    if h != site_func.encode_id(request.args.get('id'), bot.salt):
        return 'Для доступа к редактированию напоминаний, пожалуйста, запросите ссылку в боте по команде "настройки"'

    rows = site_func.get_reminders(bot)
    bad_ids = site_func.get_bad_ids(bot)
    return render_template('admin.html', rows=rows, bad_ids=bad_ids)


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False)
