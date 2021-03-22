import vk_api
import yaml
import requests
from vk_api.longpoll import VkLongPoll, VkEventType

with open('settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)
    settings = settings[0]

session = requests.Session()
token, confirmation_token = settings[0], settings[1]
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session, wait=25)
vk = vk_session.get_api()

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
   #Слушаем longpoll, если пришло сообщение то:
        if event.text == 'Первый вариант фразы' or event.text == 'Второй вариант фразы': #Если написали фразу
            if event.from_user: #Если написали в ЛС
                vk.messages.send( #Отправляем сообщение
                    user_id=event.user_id,
                    message='Ваш текст'
		)
            elif event.from_chat: #Если написали в Беседе
                vk.messages.send( #Отправляем собщение
                    chat_id=event.chat_id,
                    message='Ваш текст'
		)


@app.route('/', methods=['POST'])
def processing():
    data = json.loads(request.data)
    if 'type' not in data.keys():
        return 'not vk'
    if data['type'] == 'confirmation':
        return confirmation_token
    elif data['type'] == 'message_new':
        messageHandler.create_answer(data['object'])
        return 'ok'