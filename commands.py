from vk_api import VkApi
from vk_api.utils import get_random_id
from mysql.connector import errors as mysql

import database
import kb
import yaml
import re
import actions


def isMember(vk, token, user_id, group_id):
    if vk.groups.isMember(access_token=token, user_id=user_id, group_id=group_id):
        return 1
    return 0


with open('settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)
    user_token, group_id, editor = settings['access_token'], settings['group_id'], settings['editor']

vk_token = (VkApi(token=user_token)).get_api()


###################### BASE #############################


def editor_answer(vk, settings, config, object):
    last_message = vk.messages.getHistory(**config, group_id=settings['group_id'],
                                          count=1, offset=1, user_id=editor)
    id = last_message['items'][0]['text']
    id = id[1:(id.find("]"))]
    if object.message['text'].lower() == 'принять':
        vk_token.groups.approveRequest(group_id=group_id, user_id=id)
        vk.messages.send(**config, random_id=get_random_id(), user_id=editor,
                         message='Принято',
                         )
        vk.messages.send(**config, random_id=get_random_id(), user_id=id,
                         message='Заявка успешно принята! Не забудьте ознакомиться с правилами',
                         )
    elif object.message['text'].lower() == 'отклонить':
        vk_token.groups.removeUser(group_id=group_id, user_id=id)
        database.del_requests(id)
        vk.messages.send(**config, random_id=get_random_id(), user_id=editor,
                         message='Не принято',
                         )
        vk.messages.send(**config, random_id=get_random_id(), user_id=id,
                         message='К сожалению, заявка была отклонена. Проверь, выполнены ли требования, правильные '
                                 'ли даны ответы выше. Если ты допустил(а) ошибку, напиши "начать" и ответь на '
                                 f'вопросы заново. По всем вопросам обращайся к [id{editor}|редактору] группы',
                         )


def check_in_table(user_id):
    tables = ['create_reminder', 'del_reminders']
    result = [database.check_step(user_id, x) for x in tables]
    if result == [0, 0]:
        return 0
    else:
        if result[0] != 0:
            return tables[0]
        elif result[1] != 0:
            return tables[1]


###################### РЕДАКТОР #######################


def req(vk, config, object):
    user_id = object.message['from_id']
    result = database.show_requests()
    message = ''
    for x in result:
        vk_id, vk_name, id, name, position = str(x[0]), x[2], str(x[3]), x[4].title(), x[5]
        message = message + position + '\n|-\n| [[*id' + vk_id + '|' + vk_name + ']]\n| [*' + name + '|' + id + ']\n| [https://catwar.su/cat' + id + ']\n'
    if message == '':
        message = 'Заявок нет'
    else:
        database.del_requests()
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id, dont_parse_links=1,
                     message=message,
                     )


###################### START ##########################


def create_reminder(vk, config, object):
    user_id = object.message['from_id']
    step = int(database.check_step(user_id, 'create_reminder'))

    if step == 0:  # нажал создать
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message='Напиши название деятельности, например, патруль',
                         keyboard=kb.kb_exit()
                         )
        database.add_step(user_id, 1, 'create_reminder')

    if step == 1:  # ввел название
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'create_reminder')
        else:
            if not re.search('[^Ёа-я ]', object.message['text'], flags=re.IGNORECASE):
                for c in actions.action_list:
                    if (object.message['text']).lower() in c.vars:
                        database.add_action(user_id, c.vars[0], None)
                        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                         message='Выбери время:',
                                         keyboard=kb.kb_action(c.times)
                                         )
                        database.add_step(user_id, 2, 'create_reminder')

                else:
                    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                     message='Не удалось распознать, попробуй назвать деятельность по-другому')
            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Проверь правильность ввода')

    if step == 2:  # ввел время
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'create_reminder')
            database.del_all(user_id)
        else:
            if not re.search('[^:0-9]', object.message['text'], flags=re.IGNORECASE):
                try:
                    database.add_action(user_id, None, object.message['text'])
                except mysql.IntegrityError:
                    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                     message='У тебя уже есть такое напоминание')
                else:
                    database.del_step(user_id, 'create_reminder')
                    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                     message='Успешно!',
                                     )
            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Проверь правильность ввода')


def show_reminders(vk, config, object):
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


def del_reminder(vk, config, object):
    user_id = object.message['from_id']
    step = int(database.check_step(user_id, 'del_reminders'))

    if step == 0:  # нажал удалить
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message='Хочешь удалить одно напоминание или всю рассылку?',
                         keyboard=kb.kb_del(),
                         )
        database.add_step(user_id, 1, 'del_reminders')

    if step == 1:  # ввел название
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'del_reminders')
        else:
            if object.message['text'].lower() == 'одно' or object.message['text'] == '1':
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Напиши название деятельности, например, патруль',
                                 )
                database.add_step(user_id, 2, 'del_reminders')
            elif object.message['text'].lower() == 'все' or object.message['text'].lower() == 'всё':
                database.del_step(user_id, 'del_reminders')
                database.del_all(user_id)
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Все напоминания успешно удалены',
                                 )
            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Не удалось распознать, попробуй написать по-другому',
                                 )

    if step == 2:
        if not re.search('[^Ёа-я ]', object.message['text'].lower(), flags=re.IGNORECASE):
            for c in actions.action_list:
                if object.message['text'].lower() in c.vars:
                    name = c.get_var_name()
                    database.del_add_action(user_id, name)
                    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                     message='Выбери время:',
                                     keyboard=kb.kb_action(c.times),
                                     )
                    database.add_step(user_id, 3, 'del_reminders')
                    break
            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Не удалось распознать, попробуй назвать деятельность по-другому')
        else:
            vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                             message='Проверь правильность ввода')

    if step == 3:
        time = object.message['text']
        if not re.search('[^:0-9]', time, flags=re.IGNORECASE):
            get_action = database.del_get_action(user_id)
            action = eval(f'actions.{get_action}.vars[0]')
            database.del_action(user_id, action, time)
            database.del_step(user_id, 'del_reminders')
            vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                             message=(
                                     action.title()
                                     + ' в ' + time + ' удален(а) или у тебя не было такого напоминания'
                                     )
                             )

        else:
            vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                             message='Проверь правильность ввода')


def start(vk, config, object):
    user_id = object.message['from_id']
    if user_id == editor:
        perm = 1
    else:
        perm = 0
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Выбери одну из функций:',
                     keyboard=kb.kb_start(perm),
                     )
