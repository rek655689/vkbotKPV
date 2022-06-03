from flask import Flask, request, render_template
from bot import Bot
from user import User
import site_func
from check_time import check_time
import json
from os import system
from hashlib import sha1
from threading import Thread

system('start /b lt -p 5000 --subdomain vkbotkpv')

app = Flask(__name__)
app.config.from_envvar('SETTINGS')


# vk.groups.setCallbackSettings(group_id=203355465, server_id=18, message_new=1, message_deny=1, message_event=1)
# 18 server_id = vk.groups.addCallbackServer(group_id=203355465, url='https://vkbotkpv.loca.lt', title='Сервер 2',
#                                         secret_key='7pOZZhEE4u')

bot = Bot(app.config)
Thread(target=check_time, args=(bot, app.config['GROUP_ID']), daemon=True).start()


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
    data = json.loads(request.data)
    response = site_func.handler(bot, data)
    return 'ok' if response is False else response


@app.route('/settings', methods=['GET'])
def settings():
    h = request.args.get('h')
    if h != sha1(bot.salt.encode() + request.args.get('id').encode()).hexdigest()[:-2]:
        return 'Для доступа к редактированию напоминаний, пожалуйста, запросите ссылку в боте по команде "настройки"'

    reminders = site_func.get_reminders(bot, request.args.get('id'))
    actions = site_func.get_actions(bot)
    unique_now = site_func.get_unique_now(bot, request.args.get('id'))
    unique_available = site_func.get_unique_available(bot, request.args.get('id'))
    return render_template('settings.html', rows_now=reminders, rows_available=actions,
                           rows_unique_now=unique_now, rows_unique_available=unique_available)


@app.route('/admin', methods=['GET'])
def admin():
    return render_template('admin.html', name='Rek')


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False)
