import kb, yaml
from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotEventType
import database

with open('settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)
user_token, group_id, editor = settings['access_token'], settings['group_id'], settings['editor']
vk_token = (VkApi(token=user_token)).get_api()


def steps(vk, longpoll, config, object):
    user_id = object.message['from_id']

    # ПРОВЕРКА ЗАЯВКИ
    requests = vk_token.groups.getRequests(group_id=group_id)
    if user_id not in requests['items']:
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message='Подай, пожалуйста, заявку в группу',
                         )
        var = True
        while var:
            requests = vk_token.groups.getRequests(group_id=group_id)
            var = user_id not in requests['items']

    # ДОЛЖНОСТЬ
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Если твоей должности нет в списке, то просто напиши её',
                     keyboard=kb.kb_position()
                     )
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.object.message['from_id'] == user_id:
                event = event
                break
    position = event.object.message['text'].lower()

    # ЕСЛИ КОТЕНОК
    last_name = ''
    if position == 'котенок' or position == 'котёнок':
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message='Напиши имя, которое ты носил(а) будучи стражем/охотником в прошлой жизни',
                         )
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.object.message['from_id'] == user_id:
                    event = event
                    break
        last_name = event.object.message['text'].lower()

    # АЙДИ
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Введи свой ID на CatWar',
                     )
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.object.message['from_id'] == user_id:
                event = event
                break
    id = event.object.message['text']

    # ИМЯ
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Введи своё имя на CatWar',
                     )
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.object.message['from_id'] == user_id:
                event = event
                break
    name = (event.object.message['text']).title()

    # ПРОФИЛЬ
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Отправь скриншот своего профиля со страницы Мой кот/Моя кошка',
                     )
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.object.message['from_id'] == user_id:
                event = event
                break
    url = (((((event.object.message['attachments'])[0])['photo'])['sizes'])[-1])['url']

    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Отлично! Твоя заявка была отправлена на проверку редактору группы, осталось немного '
                             'подождать',
                     )

    # ОТПРАВКА РЕДАКТОРУ
    vk.messages.send(**config, random_id=get_random_id(), user_id=editor,
                     message=name + last_name +'\n' + position + '\nhttps://catwar.su/cat' + id + '\n' + url,
                     keyboard=kb.kb_request()
                     )

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.object.message['from_id'] == editor:
                if event.object.message['text'].lower() == 'принять' or event.object.message['text'].lower() == 'отклонить':
                    break

    if event.object.message['text'].lower() == 'принять':
        vk_token.groups.approveRequest(group_id=group_id, user_id=user_id)
        vk_name = vk.users.get(user_ids=user_id, fields='first_name, last_name')[0]
        vk_name = vk_name['first_name'] + ' ' + vk_name['last_name']
        database.add_member(user_id, vk_name, id, name, position)
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message='Принято! Не забудь ознакомиться с правилами',
                         )
