from kb import Keyboard
ADMIN = ['creator', 'administrator']
EDITOR = ['creator', 'administrator', 'editor', 'moderator']
ANY = ['creator', 'administrator', 'editor', 'moderator', 'advertiser', 'user']


class Command:
    """
    Класс-родитель для всех команд
    """

    # массив строк с вариациями текста, по которым будет вызвана команда
    name: list = []

    # описание, показываемое при вызове команды "помощь"
    description = None

    # уровень доступа
    access = None

    # название таблицы, в которую записываются этапы
    table = None

    @classmethod
    def run(cls, bot, message) -> dict and bool:
        pass
