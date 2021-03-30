from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotEventType
from actions import action_list, kb
import introduction, database, yaml


def isMember(vk, token, user_id, group_id):
    if vk.groups.isMember(access_token=token, user_id=user_id, group_id=group_id):
        return 1
    return 0


with open('settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)
    editor = settings['editor']


###################### BASE #############################

def intr(vk, longpoll, config, object):
    user_id = object.message['from_id']
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Если ты состоишь в клане, занимаешь должность не ниже будущего (или был(а) '
                             'стражем/охотником в прошлой жизни) и хочешь вступить в группу, то нажми соответствующую '
                             'кнопку',
                     keyboard=kb.kb_introduction()
                     )

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.object.message['from_id'] == user_id:
                event = event
                break

    if event.object.message['text'].lower() == 'вступить':
        introduction.steps(vk, longpoll, config, event.object)


def dont_know(vk, config, object):
    vk.messages.send(**config, random_id=get_random_id(), user_id=object.message['from_id'],
                     message='Прости, не понимаю тебя. Напиши "начать", чтобы ознакомиться со списком функций',
                     )


###################### START ##########################

def create_reminder(vk, longpoll, config, object):
    user_id = object.message['from_id']
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Напиши название деятельности, например, патруль',
                     )
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.object.message['from_id'] == user_id:
                event = event
                break
    for c in action_list:
        if (event.object.message['text']).lower() in c.vars:
            c.add(vk, longpoll, config, event.object)


def show_reminder(vk, longpoll, config, object):
    user_id = object.message['from_id']
    result = database.show_reminders(user_id)
    message = ''
    for x in result:
        message = message + x[1] + ' — ' + x[0] + '\n'
    if message == '':
        message = 'Напоминаний нет'
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message=message,
                     )


def del_reminder(vk, longpoll, config, object):
    user_id = object.message['from_id']
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Хочешь удалить одно напоминание или всю рассылку?',
                     keyboard=kb.kb_del(),
                     )
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.object.message['from_id'] == user_id:
                event = event
                break
    if event.object.message['text'].lower() == 'одно':
        del_one(vk, longpoll, config, object)
    elif event.object.message['text'].lower() == 'все' or event.object.message['text'].lower() == 'всё':
        del_all(vk, longpoll, config, object)


def del_one(vk, longpoll, config, object):
    user_id = object.message['from_id']
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Напиши название деятельности, например, патруль',
                     )
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.object.message['from_id'] == user_id:
                event = event
                break
    for c in action_list:
        if (event.object.message['text']).lower() in c.vars:
            c.delete(vk, longpoll, config, event.object)


def del_all(vk, config, object):
    user_id = object.message['from_id']
    database.del_all(user_id)
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Все напоминания успешно удалены',
                     )


def request(vk, config, object):
    user_id = object.message['from_id']
    result = database.show_requests()
    message = ''
    for x in result:
        vk_id, vk_name, id, name, position = str(x[0]), x[1], str(x[2]), x[3], x[4]
        message = message + position + '\n|-\n| [[*id' + vk_id + '|' + vk_name + ']]\n| [*' + name + '|' + id + ']\n| [https://catwar.su/cat' + id + ']\n'
    if message == '':
        message = 'Заявок нет'
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id, dont_parse_links=1,
                     message=message,
                     )
    database.del_requests()


def start(vk, longpoll, config, object):
    user_id = object.message['from_id']
    if user_id == editor:
        perm = 1
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Выбери одну из функций:',
                     keyboard=kb.kb_start(perm),
                     )
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.object.message['from_id'] == user_id:
                event = event
                break

    if (event.object.message['text']).lower() == 'создать напоминание':
        create_reminder(vk, longpoll, config, event.object)

    elif (event.object.message['text']).lower() == 'мои напоминания':
        show_reminder(vk, longpoll, config, event.object)

    elif (event.object.message['text']).lower() == 'удалить напоминания':
        del_reminder(vk, longpoll, config, event.object)

    elif (event.object.message['text']).lower() == 'заявки' and event.object.message['from_id'] == editor:
        request(vk, config, event.object)

    else:
        dont_know(vk, config, event.object)
