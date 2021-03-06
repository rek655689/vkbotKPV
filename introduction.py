from vk_api import VkApi
from vk_api.utils import get_random_id
from settings import *
import managers
from threading import Timer

import database
import kb
import re


def intr(vk, config, object):
    vk_token = (VkApi(token=access_token)).get_api()
    user_id = object.message['from_id']
    step = int(database.check_step(user_id, 'intr'))

    if step == 0:  # не нажал
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message='Если ты состоишь в клане, занимаешь должность не ниже будущего (или был(а) '
                                 'стражем/охотником в прошлой жизни) и хочешь вступить в группу, то нажми '
                                 'соответствующую кнопку (или напиши "вступить").\nНа любом этапе ты можешь выйти из '
                                 'диалога с помощью кнопки или слова "выйти".',
                         keyboard=kb.kb_introduction()
                         )
        database.add_step(user_id, 1, 'intr')

    if step == 1:  # нажал вступить, проверка заявки
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'intr')
            vk.messages.markAsRead(peer_id=user_id)
        elif object.message['text'].lower() == 'вступить' or object.message['text'].lower() == 'готово':
            requests = vk_token.groups.getRequests(group_id=group_id)
            if user_id not in requests['items']:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Подай, пожалуйста, заявку в группу. После этого нажми или напиши "готово"',
                                 keyboard=kb.kb_intr_req()
                                 )
            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Если твоей должности нет в списке ниже, то просто напиши её',
                                 keyboard=kb.kb_position()
                                 )
                database.add_step(user_id, 2, 'intr')

    if step == 2:  # получение должности
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'intr')
            vk.messages.markAsRead(peer_id=user_id)
        else:
            position = object.message['text'].lower()

            if not re.search('[^Ёа-я ]', position, flags=re.IGNORECASE):
                database.add_inf(user_id, 'position', position)

                if position == 'котенок' or position == 'котёнок':
                    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                     message='Напиши имя, которое ты носил(а) будучи стражем/охотником в прошлой жизни',
                                     keyboard=kb.kb_exit())
                    database.add_step(user_id, 22, 'intr')
                else:
                    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                     message='Введи свой ID на CatWar',
                                     keyboard=kb.kb_exit())
                    database.add_step(user_id, 3, 'intr')
            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Проверь правильность ввода',
                                 keyboard=kb.kb_exit())

    if step == 22:  # получение предыдущего имени котёнка
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'intr')
            vk.messages.markAsRead(peer_id=user_id)
        else:
            last_name = object.message['text'].lower().title()
            if not re.search('[^Ёа-я ]', last_name, flags=re.IGNORECASE):
                database.add_inf(user_id, 'last_name', last_name)

                database.add_step(user_id, 3, 'intr')
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Введи свой ID на CatWar',
                                 keyboard=kb.kb_exit())
            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Проверь правильность ввода',
                                 keyboard=kb.kb_exit())

    if step == 3:  # получение айди
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'intr')
            vk.messages.markAsRead(peer_id=user_id)
        else:
            id = object.message['text']
            if not re.search('[^0-9]', id, flags=re.IGNORECASE):
                if id == '172073':
                    vk_token.groups.removeUser(group_id=group_id, user_id=user_id)
                    database.del_requests(id)
                    database.del_step(id, 'intr')
                    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                     message='К сожалению, по некоторым причинам заявка была отклонена. По всем '
                                             f'вопросам обращайся к [id{editor}]|редактору] группы '
                                     )
                else:
                    database.add_inf(user_id, 'id', id)
                    database.add_step(user_id, 4, 'intr')
                    vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                     message='Введи своё имя на CatWar',
                                     keyboard=kb.kb_exit())
            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Проверь правильность ввода',
                                 keyboard=kb.kb_exit())

    if step == 4:  # получение имени
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'intr')
            vk.messages.markAsRead(peer_id=user_id)
        else:
            name = object.message['text'].lower().title()
            if not re.search('[^Ёа-я ]', name, flags=re.IGNORECASE):
                database.add_inf(user_id, 'name', name)
                database.add_step(user_id, 5, 'intr')
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Отправь скриншот своего профиля со страницы Мой кот/Моя кошка',
                                 keyboard=kb.kb_exit())
            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Проверь правильность ввода',
                                 keyboard=kb.kb_exit())

    if step == 5:  # получение скрина
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'intr')
            vk.messages.markAsRead(peer_id=user_id)
        else:
            if not object.message['attachments']:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Отправь скриншот своего профиля со страницы Мой кот/Моя кошка',
                                 keyboard=kb.kb_exit())
            else:
                message_id = object.message['id']
                database.add_step(user_id, 6, 'intr')
                vk_name = vk.users.get(user_ids=user_id, fields='first_name, last_name')[0]
                vk_name = vk_name['first_name'] + ' ' + vk_name['last_name']
                database.add_inf(user_id, 'vk_name', vk_name)
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Твоя заявка отправлена, осталось дождаться её одобрения.',
                                 )

                # ОТПРАВКА РЕДАКТОРУ
                result = database.get_req(user_id)
                for x in result:
                    id, name, last_name, position = x[0], str(x[1]), x[2], str(x[3])
                if last_name is None:
                    last_name = ''
                else:
                    last_name = '(ранее ' + str(last_name) + ')'

                last_manager_id = managers.last_manager(vk)

                req_message_id = vk.messages.send(**config, random_id=get_random_id(), user_id=last_manager_id,
                                                  message=f"[{user_id}] \n {name} {last_name} \n {position} \n https://catwar.su/cat{id}",
                                                  forward_messages=message_id,
                                                  keyboard=kb.kb_request(user_id)
                                                  )
                database.add_ids(req_message_id, last_manager_id, user_id)

                def send_all_managers():
                    if not vk.groups.isMember(access_token=token, user_id=user_id, group_id=group_id):
                        for manager_id in managers.get(vk)[1]:
                            if manager_id == last_manager_id:
                                continue
                            req_message_id = vk.messages.send(**config, random_id=get_random_id(), user_id=manager_id,
                                                              message=f"[{user_id}] \n {name} {last_name} \n {position} \n https://catwar.su/cat{id}",
                                                              forward_messages=message_id,
                                                              keyboard=kb.kb_request(user_id)
                                                              )
                            database.add_ids(req_message_id, last_manager_id, user_id)

                t = Timer(600.0, send_all_managers)
                t.start()

    if step == 6:  # ожидание одобрения
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message='Твоя заявка отправлена, осталось дождаться её одобрения.',
                         )
