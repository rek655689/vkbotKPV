from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotEventType
from actions import action_list,kb

def isMember(vk, token, user_id, group_id):
    if vk.groups.isMember(access_token=token, user_id=user_id, group_id=group_id):
        return 1
    return 0


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


def start(vk, longpoll, config, object):
    vk.messages.send(**config, random_id=get_random_id(), user_id=object.message['from_id'],
                     message='Выбери одну из функций:',
                     keyboard= kb.kb_start(),
                     )
    event = longpoll.check()[-1]
    while event.type != VkBotEventType.MESSAGE_NEW:
        event = list(longpoll.check())
        event = event[-1]
    if (event.object.message['text']).lower() == 'создать напоминание':
        create_reminder(vk, longpoll, config, event.object)
    if (object.message['text']).lower() == 'мои напоминания':
        vk.messages.send(**config, random_id=get_random_id(), user_id=object.message['from_id'],
                        message='Выбери одну из функций:',  # TODO
                        keyboard=kb.kb_start(),
                        )
    if (object.message['text']).lower() == 'удалить напоминание':
        vk.messages.send(**config, random_id=get_random_id(), user_id=object.message['from_id'],
                        message='Выбери одну из функций:',  # TODO
                        keyboard=kb.kb_start(),
                        )



#создать напоминание
#мои напоминания
#удалить напоминание