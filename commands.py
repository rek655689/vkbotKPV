from vk_api import VkApi
from vk_api.utils import get_random_id
from mysql.connector import errors as mysql
from settings import *

import database
import kb
import re
import actions
import update_pages


def isMember(vk, token, user_id, group_id):
    if vk.groups.isMember(access_token=token, user_id=user_id, group_id=group_id):
        return 1
    return 0


###################### BASE #############################

def help(vk, config, object):
    user_id = object.message['from_id']
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='С помощью данного бота ты можешь поставить напоминание за несколько минут до любой '
                             'имеющейся в клане деятельности.\n'
                             'На любом этапе для управления можно использовать специальную клавиатуру/кнопки или писать'
                             ' команды словами (без тире и других символов).\n'
                             'Сейчас тебе доступны следующие команды:\n'
                             '- создать напоминание — начнётся диалог для создания рассылки, где тебе необходимо '
                             'будет указать деятельность, её время и за сколько минут нужно напоминать;\n '
                             '- мои напоминания — покажет всю инфорамцию об установленных тобой напоминаниях;\n'
                             '- удалить напоминания — жми сюда, если нужно удалить одну или несколько рассылок;\n'
                             '- таблица занятости — здесь можешь узнать расписание всех клановых деятельностей и '
                             'узнать на что ещё можно поставить напоминания;\n'
                             '- предложить идею — если у тебя есть замечания по поводу работы бота или идею по его '
                             'улучшению, то по этой команде ты можешь получить ссылку на анонимную гугл-форму.\n'
                             'Если возникнут вопросы по клану — в контактах группы есть ссылки на представителей верха.'
                             'По поводу технических неполадок обращайся к одному из редакторов '
                             f'([id478936081|Вздох Восхищения] или [id{editor}|Пышный])',
                     )


def check_in_table(vk, config, object):
    user_id = object.message['from_id']
    tables = ['create_reminder', 'del_reminders']
    result = [database.check_step(user_id, x) for x in tables]
    if result == [0, 0]:
        return 0
    else:
        if result[0] != 0:
            return tables[0]
        elif result[1] != 0:
            return tables[1]


def table(vk, config, object):
    user_id = object.message['from_id']
    attachment = 'photo-165101106_457239755'
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Собрания - 18:00 (среда - 19:00, воскресенье - 16:00)\n'
                             'Ветки - 12:00, 16:00\n'
                             'Самая Яркая Ночь - 18:00 в последнее воскресенье месяца',
                     attachment=attachment
                     )


def idea(vk, config, object):
    user_id = object.message['from_id']
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Если у тебя есть какие-либо замечания, предложения, идеи и пр., то ты можешь абсолютно '
                             'анонимно выразить их здесь:\n>>https://docs.google.com/forms/d/13j-jeLwJngqZUReIn7RscG4GC'
                             '9g4CqSQ42hNWnkzrXg/edit?usp=sharing << '
                     )


###################### РЕДАКТОР #######################


def editor_answer(function_to_decorate):
    def editor_answer_base(vk, config, object):
        vk_token = (VkApi(token=access_token)).get_api()
        i = 1
        id, member = '1', 1
        while id[0] != '[' and member == 1:
            last_message = vk.messages.getHistory(**config, group_id=group_id,
                                                  count=1, offset=i, user_id=editor)
            id = last_message['items'][0]['text']
            i += 1
            if id[0] == '[':
                id = id[1:(id.find("]"))]
                member = isMember(vk, token=token, group_id=group_id, user_id=id)
        function_to_decorate(vk_token, vk, config, id)
    return editor_answer_base


@editor_answer
def accept(vk_token, vk, config, id):
    vk_token.groups.approveRequest(group_id=group_id, user_id=id)
    vk.messages.send(**config, random_id=get_random_id(), user_id=editor,
                     message='Принят ' + id,
                     )
    vk.messages.send(**config, random_id=get_random_id(), user_id=id,
                     message='Заявка успешно принята! Не забудь ознакомиться с правилами:\n'
                             '>> https://vk.com/page-165101106_55801147 <<\n\nНапиши любое сообщение, '
                             'чтобы перейти к меню бота, или "помощь", чтобы узнать больше',
                     )


@editor_answer
def reject(vk_token, vk, config, id):
    vk_token.groups.removeUser(group_id=group_id, user_id=id)
    database.del_requests(id)
    database.del_step(id, 'intr')
    vk.messages.send(**config, random_id=get_random_id(), user_id=editor,
                     message='Не принято',
                     )
    vk.messages.send(**config, random_id=get_random_id(), user_id=id,
                     message='К сожалению, заявка была отклонена. Проверь, выполнены ли требования, правильные '
                             'ли даны ответы выше. Если ты допустил(а) ошибку, напиши "начать" и ответь на '
                             f'вопросы заново. По всем вопросам обращайся к [id{editor}|редактору] группы',
                     )


def req(vk, config, object):
    user_id = object.message['from_id']
    result = object.message['text'].lower()[19::]
    vk_id, vk_name, name, id, position = result.split(', ')
    update_pages.add_member(vk_id, vk_name, name, id, position)
    message = 'Внесено'
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id, message=message)


###################### START ##########################


def create_reminder(vk, config, object):
    user_id = object.message['from_id']
    step = int(database.check_step(user_id, 'create_reminder'))

    if step == 0:  # нажал создать
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message='Ты можешь создать напоминание за 5 или 10 минут до какой-либо деятельности, '
                                 'для этого тебе необходимо написать её название. Можно использовать разные варианты, '
                                 'например:\n— пограничный патруль\n— оп\n— мохосбор\nЕсли твоё сообщение не читается, '
                                 'попробуй другую формулировку, например, указанную в таблице занятости',
                         keyboard=kb.kb_exit()
                         )
        database.add_step(user_id, 1, 'create_reminder')

    if step == 1:  # ввел название
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'create_reminder')
            start(vk, config, object)
        else:
            if not re.search('[^Ёа-я ]', object.message['text'], flags=re.IGNORECASE):
                for c in actions.action_list:
                    if (object.message['text']).lower() in c.vars:
                        database.add_action(user_id, c.vars[0], None, None)
                        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                         message='Введи время:',
                                         keyboard=kb.kb_action(c.times)
                                         )
                        database.add_step(user_id, 2, 'create_reminder')

            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Проверь правильность ввода',
                                 keyboard=kb.kb_exit())

    if step == 2:  # ввел время
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'create_reminder')
            database.del_all(user_id, False)
            start(vk, config, object)
        else:
            if not re.search('[^:0-9]', object.message['text'], flags=re.IGNORECASE) and len(
                    object.message['text']) == 5 and (object.message['text'])[2] == ':':
                database.add_action(user_id, None, object.message['text'], None)
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='За сколько минут напоминать? (5 или 10)',
                                 keyboard=kb.kb_section()
                                 )
                database.add_step(user_id, 3, 'create_reminder')

            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Проверь правильность ввода',
                                 keyboard=kb.kb_exit())

    if step == 3:  # ввел отрезок
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'create_reminder')
            database.del_all(user_id, False)
            start(vk, config, object)
        else:
            if not re.search('[^0-9]', object.message['text'], flags=re.IGNORECASE) and len(
                    object.message['text']) <= 2:
                try:
                    database.add_action(user_id, None, None, object.message['text'])
                except mysql.IntegrityError:
                    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                     message='У тебя уже есть такое напоминание')
                    database.del_step(user_id, 'create_reminder')
                    start(vk, config, object)
                else:
                    database.del_step(user_id, 'create_reminder')
                    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                     message='Успешно!',
                                     )
            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Проверь правильность ввода',
                                 keyboard=kb.kb_exit())


def show_reminders(vk, config, object):
    user_id = object.message['from_id']
    result = database.show_reminders(user_id)
    message = ''
    for x in result:
        message = f'{message}{x[1]} — {x[0]} (за {x[2]} минут)\n'
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

    if step == 1:  # ввел
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'del_reminders')
            start(vk, config, object)
        else:
            if object.message['text'].lower() == 'одно' or object.message['text'] == '1':
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Напиши название деятельности, например, патруль',
                                 )
                database.add_step(user_id, 2, 'del_reminders')
            elif object.message['text'].lower() == 'все' or object.message['text'].lower() == 'всё':
                database.del_step(user_id, 'del_reminders')
                database.del_all(user_id, True)
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Все напоминания успешно удалены',
                                 )

    if step == 2:
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'del_reminders')
            start(vk, config, object)
        else:
            if not re.search('[^Ёа-я ]', object.message['text'].lower(), flags=re.IGNORECASE):
                for c in actions.action_list:
                    if object.message['text'].lower() in c.vars:
                        name = c.get_var_name()
                        database.del_add_action(user_id, name)
                        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                         message='Введи время:',
                                         keyboard=kb.kb_action(c.times),
                                         )
                        database.add_step(user_id, 3, 'del_reminders')
            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Проверь правильность ввода',
                                 keyboard=kb.kb_exit())

    if step == 3:
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'del_reminders')
            start(vk, config, object)
        else:
            time = object.message['text']
            if not re.search('[^:0-9]', time, flags=re.IGNORECASE) and len(object.message['text']) == 5 and \
                    (object.message['text'])[2] == ':':
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
                                 message='Проверь правильность ввода',
                                 keyboard=kb.kb_exit())


def start(vk, config, object):
    user_id = object.message['from_id']
    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                     message='Выбери одну из функций:',
                     keyboard=kb.kb_start(),
                     )


editor_commands = {'принять': accept, 'отклонить': reject}
user_commands = {'помощь': help, 'создать напоминание': create_reminder, 'мои напоминания': show_reminders,
                 'удалить напоминания': del_reminder, 'таблица занятости': table, 'предложить идею': idea}
