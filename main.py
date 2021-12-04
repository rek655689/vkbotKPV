from bot import Bot
from database import Database
from user import User
import flask
import json
import time

from vk_api.bot_longpoll import VkBotEventType


from flask import Flask

app = Flask(__name__)
app.config.from_envvar('SETTINGS')


# vk.groups.setCallbackSettings(group_id=203355465, server_id=18, message_new=1, message_deny=1, message_event=1)
# 18 server_id = vk.groups.addCallbackServer(group_id=203355465, url='https://vkbotkpv.loca.lt', title='Сервер 2',
#                                         secret_key='7pOZZhEE4u')


bot = Bot(app)
db = Database(app.config['DATABASE'])


@app.route('/', methods=['POST'])
def processing():
    data = json.loads(flask.request.data)
    if data['secret'] != app.config['SECRET_KEY']:
        return 'not vk'
    if data['type'] == 'confirmation':
        return '494a1188'
    if data['type'] == 'message_new': # TODO: or data['type'] == 'message_event':
        user = User(db, data['object']['message']['from_id'], app)
        if user.
        bot.commands(data['object']['message']['text'].lower(), user, db)
    if data['type'] == 'group_leave':
        return 'not ok'  # TODO
    return 'ok'


if __name__ == '__main__':
    app.run()
