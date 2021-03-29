from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotEventType
from actions import action_list, kb
from vk_api import VkApi
import yaml
import introduction


def isMember(vk, token, user_id, group_id):
    if vk.groups.isMember(access_token=token, user_id=user_id, group_id=group_id):
        return 1
    return 0


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


def dont_know():
    with open('settings.yaml', encoding='utf8') as f:
        settings = yaml.safe_load(f)
    user_token, group_id = settings['access_token'], settings['group_id']

    vk = VkApi(token=user_token)
    vk = vk.get_api()
    page = vk.pages.get(owner_id=-group_id, page_id=56341561, need_source=1)
    print(page['source'])
    # vk.messages.send(**config, random_id=get_random_id(), user_id=object.message['from_id'],
    #     message='Прости, не понимаю тебя. Напиши "начать" чтобы ознакомиться со списком функций',
    #    )


###################### START ##########################

def create_reminder(vk, longpoll, config, object):
    vk.messages.send(**config, random_id=get_random_id(), user_id=object.message['from_id'],
                     message='Напиши название деятельности, например, патруль',
                     )
    event = longpoll.check()[-1]
    while event.type != VkBotEventType.MESSAGE_NEW:
        event = list(longpoll.check())
        event = event[-1]
    for c in action_list:
        if (event.object.message['text']).lower() in c.vars:
            c.process(vk, longpoll, config, event.object)


def show_reminder(vk, longpoll, config, object):
    database.show_reminder()  # TODO


def del_reminder(vk, longpoll, config, object):
    vk.messages.send(**config, random_id=get_random_id(), user_id=object.message['from_id'],
                     message='Хочешь удалить одно напоминание или всю рассылку?',
                     keyboard=kb.kb_del(),
                     )
    event = longpoll.check()[-1]
    while event.type != VkBotEventType.MESSAGE_NEW:
        event = list(longpoll.check())
        event = event[-1]
    if event.object.message['text'].lower() == 'одно':
        del_all(vk, longpoll, config, object)  # TODO
    elif event.object.message['text'].lower() == 'все' or event.object.message['text'].lower() == 'всё':
        del_all(vk, longpoll, config, object)  # TODO


def start(vk, longpoll, config, object):
    vk.messages.send(**config, random_id=get_random_id(), user_id=object.message['from_id'],
                     message='Выбери одну из функций:',
                     keyboard=kb.kb_start(),
                     )
    event = longpoll.check()[-1]
    while event.type != VkBotEventType.MESSAGE_NEW:
        event = list(longpoll.check())
        event = event[-1]

    if (event.object.message['text']).lower() == 'создать напоминание':
        create_reminder(vk, longpoll, config, event.object)

    elif (event.object.message['text']).lower() == 'мои напоминания':
        show_reminder(vk, longpoll, config, event.object)

    elif (event.object.message['text']).lower() == 'удалить напоминания':
        del_reminder(vk, longpoll, config, event.object)
