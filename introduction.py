from vk_api import VkApi
from vk_api.utils import get_random_id

import database
import kb
import yaml
import re

with open('./settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)
user_token, group_id, editor = settings['access_token'], settings['group_id'], settings['editor']
vk_token = (VkApi(token=user_token)).get_api()


def intr(vk, config, object):
    user_id = object.message['from_id']
    step = int(database.check_step(user_id, 'intr'))

    if step == 0:  # не нажал
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message='Если ты состоишь в клане, занимаешь должность не ниже будущего (или был(а) '
                                 'стражем/охотником в прошлой жизни) и хочешь вступить в группу, то нажми '
                                 'соответствующую '
                                 'кнопку',
                         keyboard=kb.kb_introduction()
                         )
        database.add_step(user_id, 1, 'intr')

    if step == 1:  # нажал вступить, проверка заявки
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'intr')
        elif object.message['text'].lower() == 'вступить' or object.message['text'].lower() == 'готово':
            requests = vk_token.groups.getRequests(group_id=group_id)
            if user_id not in requests['items']:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Подай, пожалуйста, заявку в группу',
                                 keyboard=kb.kb_intr_req()
                                 )
            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Если твоей должности нет в списке, то просто напиши её',
                                 keyboard=kb.kb_position()
                                 )
                database.add_step(user_id, 2, 'intr')

    if step == 2:  # получение должности
        if object.message['text'].lower() == 'выйти':
            database.del_step(user_id, 'intr')
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
        else:
            id = object.message['text']
            if not re.search('[^0-9]', id, flags=re.IGNORECASE):
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
        else:
            if object.message['attachments']:
                url = (((((object.message['attachments'])[0])['photo'])['sizes'])[-1])['url']
                database.add_step(user_id, 6, 'intr')
                vk_name = vk.users.get(user_ids=user_id, fields='first_name, last_name')[0]
                vk_name = vk_name['first_name'] + ' ' + vk_name['last_name']
                database.add_inf(user_id, 'vk_name', vk_name)
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Твоя заявка была отправлена редактору группы, осталось дождаться её одобрения',
                                 )
            else:
                vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                                 message='Отправь скриншот своего профиля со страницы Мой кот/Моя кошка',
                                 keyboard=kb.kb_exit())

            # ОТПРАВКА РЕДАКТОРУ
            result = database.get_req(user_id)
            for x in result:
                id, name, last_name, position = x[0], str(x[1]), x[2], str(x[3])
            if last_name is None:
                last_name = ''
            else:
                last_name = str(last_name)
            vk.messages.send(**config, random_id=get_random_id(), user_id=editor,
                             message=f"[{user_id}] \n {name} (ранее {last_name}) \n {position} \n https://catwar.su/cat{id} \n {url}",
                             keyboard=kb.kb_request()
                             )

    if step == 6:  # ожидание одобрения
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message='Твоя заявка была отправлена редактору группы, осталось дождаться её одобрения',
                         )
