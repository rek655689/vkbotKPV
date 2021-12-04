import vk_api
from vk_api.utils import get_random_id
from requests_html import HTMLSession
from introduction import Command


def get_catwar_session(config: any) -> any:
    s = HTMLSession()
    url = 'https://catwar.su/ajax/login'
    user_agent_val = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                     'Chrome/90.0.4430.93 Safari/537.36 '
    s.headers.update({'Referer': url})
    s.headers.update({'User-Agent': user_agent_val})
    s.post(url, config)
    return s



class Bot:
    """Обработка входящих событий"""

    def __init__(self, app):
        self.vk = vk_api.VkApi(token=app.config['TOKEN']).get_api()
        self.vk_admin = vk_api.VkApi(token=app.config['ACCESS_TOKEN']).get_api()
        self.catwar_session = get_catwar_session(app.config['CATWAR'])

    def send(self, user_id: int, message: dict):
        """Отправка сообщения"""
        self.vk.messages.send(user_id=user_id, random_id=get_random_id(), **message)

    def commands(self, message: str, user, db):
        """Получение данных из обработчика команд"""
        answer = Command(message, user, db).handler()
        if answer is None:
            "Если отвечать не нужно, читаем сообщение пользователя"
            self.vk.messages.markAsRead(peer_id=user.vk_id)
        else:
            self.send(user.vk_id, answer)

