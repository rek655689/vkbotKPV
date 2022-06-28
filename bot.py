import vk_api
from vk_api.utils import get_random_id
from requests_html import HTMLSession
from command_handler import *
from database import Database


def get_catwar_session(config: any) -> any:
    """Получение объекта сессии на сайте"""
    s = HTMLSession()
    url = 'https://catwar.su/ajax/login'
    user_agent_val = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                     'Chrome/90.0.4430.93 Safari/537.36 '
    s.headers.update({'Referer': url})
    s.headers.update({'User-Agent': user_agent_val})
    s.post(url, config)
    return s


class Bot:

    def __init__(self, config):
        """
        :param config: конфигурация приложения
        """

        # объект пользователя, который взаимодействует с ботом
        self.user = None

        # объекты баз данных
        self.db = Database(config['DB_DEFAULT'])
        self.db_actions = Database(config['DB_ACTIONS'])

        # для обращения к API VK
        self.vk = vk_api.VkApi(token=config['TOKEN']).get_api()

        # для обращения к API VK от имени администратора
        self.vk_admin = vk_api.VkApi(token=config['ACCESS_TOKEN']).get_api()

        # id группы
        self.group_id: int = config['GROUP_ID']

        # сессия на сайте CatWar
        self.catwar_session: HTMLSession = get_catwar_session(config['CATWAR'])

        self.salt: str = config['SALT']

    def send_event_answer(self, event_id: int, user_id: int):
        """
        Отправка ответа на событие

        :param event_id: уникальный ID события
        :param user_id: ID пользователя
        """
        self.vk.messages.sendMessageEventAnswer(event_id=event_id, user_id=user_id, peer_id=user_id)

    def send(self, message_elements: dict, to_delete: bool):
        """
        Отправка сообщения

        :param message_elements: словарь, содержащий элементы для отправки сообщения (возможные ключи: message, keyboard, attachment)
        :param to_delete: флаг, обозначающий, надо ли в будущем удалять отправленное сообщение
        """
        try:
            message_id = self.vk.messages.send(user_id=self.user.vk_id, random_id=get_random_id(), **message_elements)
            if to_delete:
                self.db.add_row(table='sent_messages', columns=['user_id', 'message_id'],
                                values=[self.user.vk_id, message_id])

        except vk_api.exceptions.ApiError as e:
            # если пользователь запретил отправлять сообщения, то убираем его из рассылок
            if e.code == 901:
                pass #TODO: убрать пользователя из рассылок
            else:
                raise e

    def delete(self, message_id: int):
        """
        Удаление сообщения

        :param message_id: уникальный ID сообщения
        """
        try:
            self.vk.messages.delete(message_ids=str(message_id), delete_for_all=1, peer_id=self.user.vk_id)
        except vk_api.exceptions.ApiError:
            pass
        self.db.delete('sent_messages', 'message_id', message_id)

    def handler(self, data: dict):
        """
        Получение и обработка данных из обработчика команд

        :param data: объект сообщения пользователя или event
        """
        message = data['object']['message'] if data['type'] == 'message_new' else data['object']['payload']
        message_elements, to_delete = CommandHandler.response(message, self)
        if all(message_elements.values()) is False:
            # Если отвечать не нужно, читаем сообщение пользователя
            self.vk.messages.markAsRead(peer_id=self.user.vk_id)
        else:
            self.send(message_elements, to_delete)

    def get_managers(self, positions: list = None) -> list:
        """
        Получение списка ID руководства группы

        :param positions: список должностей, ID игроков с которыми надо получить; если None - все
        :return: список ID
        """
        result = []
        response = self.vk_admin.groups.getMembers(group_id=self.group_id, filter='managers')
        for x in response["items"]:
            if positions is not None and x["role"] in positions:
                result.append(x["id"])
            elif positions is None:
                result.append(x["id"])
        return result
