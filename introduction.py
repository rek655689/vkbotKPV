from vk_api import VkApi
from vk_api.utils import get_random_id
from threading import Timer
from kb import Keyboard
import random
import string


class Command:
    """Обработка команд"""

    def __init__(self, message: str, user, db):
        self.text = message
        self.user = user
        self.db = db
        self.answer = {}

    def handler(self) -> dict:
        if not self.user.member:
            self.answer = Introduction(self.text, self.user, self.db).handler()
        return self.answer


class Introduction(Command):

    def __init__(self, text, user, db):
        super().__init__(text, user, db)
        self.name = 'intr'
        self.__step = None

    @property
    def step(self) -> int:
        """Получение шага, на котором находится пользователь
        Если он ещё ничего не писал в группу, то шаг = 0"""
        if self.__step is None:
            try:
                self.__step = int(self.db.intr(self.user.vk_id, 'get', 'step')[0][0])
            except IndexError:
                self.__step = 0
        return self.__step

    def info(self) -> dict:
        self.db.intr(self.user.vk_id, 'set', 'step', 1)
        return {'message': 'Если ты состоишь в клане, занимаешь должность не ниже будущего (или был(а) '
                           'стражем/охотником в прошлой жизни) и хочешь вступить в группу, то нажми соответствующую '
                           'кнопку (или напиши слово "вступить")\nНа любом этапе ты можешь выйти из диалога с помощью '
                           'кнопки или слова "выйти"\nПри возникновении технических проблем всегда можешь обратиться к '
                           'одному из редакторов: [id478936081|Вздоху Восхищения] или [id463546943|Пышному], а по '
                           'поводу клановых вопросов тебе с радостью ответят главы, указанные в контактах группы'}

    def ask_catwar_id(self) -> dict:
        self.db.intr(self.user.vk_id, 'set', 'step', 2)
        return {'message': 'Напиши, пожалуйста, свой id на сайте CatWar',
                'keyboard': Keyboard.exit()}

    def get_catwar_id(self) -> dict:
        self.db.intr(self.user.vk_id, 'set', 'id', self.text)
        data = self.user.get_info(self.text)
        if data == 'нет имени':
            return {'message': 'Не удалось найти имя, попробуй снова'}
        elif data == 'нет должности':
            return {'message': 'Не удалось найти должность, попробуй снова'}
        else:
            self.db.intr(self.user.vk_id, 'set', 'step', 3)
            self.db.intr(self.user.vk_id, 'set', 'name', data[0])
            self.db.intr(self.user.vk_id, 'set', 'position', data[1])
            return {'message': f'Верно? (да/нет)\nИмя: {data[0]}\nДолжность: {data[1]}',
                    'keyboard': Keyboard.anket()}

    def get_last_name(self):
        self.db.intr(self.user.vk_id, 'set', 'step', 33)
        return {'message': 'Напиши, пожалуйста, имя, которое ты носил(а) будучи стражем/охотником'}

    def send_key(self) -> dict:
        self.db.intr(self.user.vk_id, 'set', 'step', 4)
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        self.user.catwar_session.post('https://catwar.su/ajax/mess_send',
                                      data={'whom': self.db.intr(self.user.vk_id, 'get', 'name')[0][0],
                                            'subject': 'Вступление в группу КПВ в ВК',
                                            'text': f'Код подтверждения: {key}'})
        self.db.intr(self.user.vk_id, 'set', 'secret_key', key.lower())
        return {'message': 'Тебе был отправлен код подтверждения. Зайди на сайт CatWar, скопируй код (только код!) из '
                           'личного сообщения и вставь сюда'}

    def accept(self) -> dict:
        self.db.intr(self.user.vk_id, 'set', 'step', 5)

        if not self.user.accept:
            return {'message': 'Подай, пожалуйста, заявку в группу, после чего напиши любое сообщение'}

        self.db.users(self.user.vk_id, 'add')

        vk_name = self.user.vk.users.get(user_ids=self.user.vk_id, fields='first_name, last_name')[0]
        vk_name = vk_name['first_name'] + ' ' + vk_name['last_name']
        self.db.users(self.user.vk_id, 'set', 'vk_name', vk_name)

        id = self.db.intr(self.user.vk_id, 'get', 'id')[0][0]
        self.db.users(self.user.vk_id, 'set', 'id', id)

        name = self.db.intr(self.user.vk_id, 'get', 'name')[0][0]
        self.db.users(self.user.vk_id, 'set', 'name', name)

        self.db.intr(self.user.vk_id, 'del')

        return {'message': 'Заявка успешно принята! Не забудь ознакомиться с правилами:\n'
                           '>> https://vk.com/page-165101106_55801147 <<\n\nНапиши любое сообщение, '
                           'чтобы перейти к меню бота, или "помощь", чтобы узнать больше'}

    def reject(self) -> dict:
        self.db.intr(self.user.vk_id, 'del')
        return {'message': 'К сожалению, код неверный. Попробуй написать любое сообщение и заполнить заявку снова'}

    def handler(self) -> dict:
        """Перенаправление на функцию в зависимости от шага"""
        if self.text == 'выйти':
            pass  # TODO: удаляем всё

        if self.step == 0:
            "Игрок впервые написал в группу"
            return self.info()

        elif self.step == 1:
            "Игрок решил/нажал вступить"
            if self.text == 'вступить':
                return self.ask_catwar_id()

        elif self.step == 2:
            "Игрок написал id"
            return self.get_catwar_id()

        elif self.step == 3:
            "Проверка верности анкеты"
            if self.text == 'да' or self.text == 'верно':
                if self.db.intr(self.user.vk_id, 'get', 'position')[0][0] == 'котёнок':
                    return self.get_last_name()
                else:
                    return self.send_key()
            elif self.text == 'нет' or self.text == 'неверно':
                return self.ask_catwar_id()

        elif self.step == 33:
            "Котёнок написал прошлое имя"
            self.db.intr(self.user.vk_id, 'set', 'last_name', self.text.title())
            message = self.user.super().send(self.user.last_editor(),
                                             {'message': f"[{self.user.vk_id}] \n {self.db.intr(self.user.vk_id, 'get', 'name')[0][0]} "
                                                         f"(ранее{self.db.intr(self.user.vk_id, 'get', 'last_name')[0][0]})"
                                                         f" \n https://catwar.su/cat{self.db.intr(self.user.vk_id, 'get', 'id')[0][0]}",
                                              'keyboard': Keyboard.request(self.db.intr(self.user.vk_id, 'get', 'id')[0][0])})

            # TODO: отправка редакторам

            #
            #
            #                 def send_all_managers():
            #                     if not vk.groups.isMember(access_token=token, user_id=user_id, group_id=group_id):
            #                         for manager_id in managers.get(vk)[1]:
            #                             if manager_id == last_manager_id:
            #                                 continue
            #                             req_message_id = vk.messages.send(**config, random_id=get_random_id(), user_id=manager_id,
            #                                                               message=f"[{user_id}] \n {name} {last_name} \n {position} \n https://catwar.su/cat{id}",
            #                                                               forward_messages=message_id,
            #                                                               keyboard=kb.kb_request(user_id)
            #                                                               )
            #                             database.add_ids(req_message_id, manager_id, user_id)
            #
            #                 t = Timer(600.0, send_all_managers)
            #                 t.start()
            return {'message': 'Твоя анкета отправлена редакторам, осталось дождаться её одобрения'}

        elif self.step == 333:
            "Проверка верности анкеты редакторами У КОТЁНКА"
            return {'message': 'Твоя анкета отправлена редакторам, осталось дождаться её одобрения'}

        elif self.step == 4:
            "Получение кода подтверждения"
            a = self.db.intr(self.user.vk_id, 'get', 'secret_key')[0][0]
            if self.text == a:
                return self.accept()
            else:
                return self.reject()

        elif self.step == 5:
            "Ожидание заявки в группу"
            return self.accept()


# def intr(vk, config, object):
#     vk_token = (VkApi(token=access_token)).get_api()
#     user_id = object.message['from_id']
#     step = int(database.check_step(user_id, 'intr'))
#
#     if step == 0:  # не нажал
#         vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                          message='Если ты состоишь в клане, занимаешь должность не ниже будущего (или был(а) '
#                                  'стражем/охотником в прошлой жизни) и хочешь вступить в группу, то нажми '
#                                  'соответствующую кнопку (или напиши "вступить").\nНа любом этапе ты можешь выйти из '
#                                  'диалога с помощью кнопки или слова "выйти".',
#                          keyboard=kb.kb_introduction()
#                          )
#         database.add_step(user_id, 1, 'intr')
#
#     if step == 1:  # нажал вступить, проверка заявки
#         if object.message['text'].lower() == 'выйти':
#             database.del_step(user_id, 'intr')
#             vk.messages.markAsRead(peer_id=user_id)
#         elif object.message['text'].lower() == 'вступить' or object.message['text'].lower() == 'готово':
#             requests = vk_token.groups.getRequests(group_id=group_id)
#             if user_id not in requests['items']:
#                 vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                  message='Подай, пожалуйста, заявку в группу. После этого нажми или напиши "готово"',
#                                  keyboard=kb.kb_intr_req()
#                                  )
#             else:
#                 vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                  message='Если твоей должности нет в списке ниже, то просто напиши её',
#                                  keyboard=kb.kb_position()
#                                  )
#                 database.add_step(user_id, 2, 'intr')
#
#     if step == 2:  # получение должности
#         if object.message['text'].lower() == 'выйти':
#             database.del_step(user_id, 'intr')
#             vk.messages.markAsRead(peer_id=user_id)
#         else:
#             position = object.message['text'].lower()
#
#             if not re.search('[^Ёа-я ]', position, flags=re.IGNORECASE):
#                 database.add_inf(user_id, 'position', position)
#
#                 if position == 'котенок' or position == 'котёнок':
#                     vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                      message='Напиши имя, которое ты носил(а) будучи стражем/охотником в прошлой жизни',
#                                      keyboard=kb.kb_exit())
#                     database.add_step(user_id, 22, 'intr')
#                 else:
#                     vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                      message='Введи свой ID на CatWar',
#                                      keyboard=kb.kb_exit())
#                     database.add_step(user_id, 3, 'intr')
#             else:
#                 vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                  message='Проверь правильность ввода',
#                                  keyboard=kb.kb_exit())
#
#     if step == 22:  # получение предыдущего имени котёнка
#         if object.message['text'].lower() == 'выйти':
#             database.del_step(user_id, 'intr')
#             vk.messages.markAsRead(peer_id=user_id)
#         else:
#             last_name = object.message['text'].lower().title()
#             if not re.search('[^Ёа-я ]', last_name, flags=re.IGNORECASE):
#                 database.add_inf(user_id, 'last_name', last_name)
#
#                 database.add_step(user_id, 3, 'intr')
#                 vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                  message='Введи свой ID на CatWar',
#                                  keyboard=kb.kb_exit())
#             else:
#                 vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                  message='Проверь правильность ввода',
#                                  keyboard=kb.kb_exit())
#
#     if step == 3:  # получение айди
#         if object.message['text'].lower() == 'выйти':
#             database.del_step(user_id, 'intr')
#             vk.messages.markAsRead(peer_id=user_id)
#         else:
#             id = object.message['text']
#             if not re.search('[^0-9]', id, flags=re.IGNORECASE):
#                 if id == '172073':
#                     vk_token.groups.removeUser(group_id=group_id, user_id=user_id)
#                     database.del_requests(id)
#                     database.del_step(id, 'intr')
#                     vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                      message='К сожалению, по некоторым причинам заявка была отклонена. По всем '
#                                              f'вопросам обращайся к [id{editor}]|редактору] группы '
#                                      )
#                 else:
#                     database.add_inf(user_id, 'id', id)
#                     database.add_step(user_id, 4, 'intr')
#                     vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                      message='Введи своё имя на CatWar',
#                                      keyboard=kb.kb_exit())
#             else:
#                 vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                  message='Проверь правильность ввода',
#                                  keyboard=kb.kb_exit())
#
#     if step == 4:  # получение имени
#         if object.message['text'].lower() == 'выйти':
#             database.del_step(user_id, 'intr')
#             vk.messages.markAsRead(peer_id=user_id)
#         else:
#             name = object.message['text'].lower().title()
#             if not re.search('[^Ёа-я ]', name, flags=re.IGNORECASE):
#                 database.add_inf(user_id, 'name', name)
#                 database.add_step(user_id, 5, 'intr')
#                 vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                  message='Отправь скриншот своего профиля со страницы Мой кот/Моя кошка',
#                                  keyboard=kb.kb_exit())
#             else:
#                 vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                  message='Проверь правильность ввода',
#                                  keyboard=kb.kb_exit())
#
#     if step == 5:  # получение скрина
#         if object.message['text'].lower() == 'выйти':
#             database.del_step(user_id, 'intr')
#             vk.messages.markAsRead(peer_id=user_id)
#         else:
#             if not object.message['attachments']:
#                 vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                  message='Отправь скриншот своего профиля со страницы Мой кот/Моя кошка',
#                                  keyboard=kb.kb_exit())
#             else:
#                 message_id = object.message['id']
#                 database.add_step(user_id, 6, 'intr')
#                 vk_name = vk.users.get(user_ids=user_id, fields='first_name, last_name')[0]
#                 vk_name = vk_name['first_name'] + ' ' + vk_name['last_name']
#                 database.add_inf(user_id, 'vk_name', vk_name)
#                 vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                                  message='Твоя заявка отправлена, осталось дождаться её одобрения.',
#                                  )
#
#                 # ОТПРАВКА РЕДАКТОРУ
#                 result = database.get_req(user_id)
#                 for x in result:
#                     id, name, last_name, position = x[0], str(x[1]), x[2], str(x[3])
#                 if last_name is None:
#                     last_name = ''
#                 else:
#                     last_name = '(ранее ' + str(last_name) + ')'
#
#                 last_manager_id = managers.last_manager(vk)
#
#                 req_message_id = vk.messages.send(**config, random_id=get_random_id(), user_id=last_manager_id,
#                                                   message=f"[{user_id}] \n {name} {last_name} \n {position} \n https://catwar.su/cat{id}",
#                                                   forward_messages=message_id,
#                                                   keyboard=kb.kb_request(user_id)
#                                                   )
#                 database.add_ids(req_message_id, last_manager_id, user_id)
#
#                 def send_all_managers():
#                     if not vk.groups.isMember(access_token=token, user_id=user_id, group_id=group_id):
#                         for manager_id in managers.get(vk)[1]:
#                             if manager_id == last_manager_id:
#                                 continue
#                             req_message_id = vk.messages.send(**config, random_id=get_random_id(), user_id=manager_id,
#                                                               message=f"[{user_id}] \n {name} {last_name} \n {position} \n https://catwar.su/cat{id}",
#                                                               forward_messages=message_id,
#                                                               keyboard=kb.kb_request(user_id)
#                                                               )
#                             database.add_ids(req_message_id, manager_id, user_id)
#
#                 t = Timer(600.0, send_all_managers)
#                 t.start()
#
#     if step == 6:  # ожидание одобрения
#         vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
#                          message='Твоя заявка отправлена, осталось дождаться её одобрения.',
#                          )
