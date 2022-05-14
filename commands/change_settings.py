from .command_class import *
from hashlib import sha1


class ChangeSettings(Command):
    name = ['настройки']
    description = ''
    access = ANY

    @classmethod
    def run(cls, bot, message) -> dict and bool:
        answer = f'Нажми на кнопку внизу, после чего напиши любое сообщение (мера безопасности: после этого сообщение ' \
                 f'со ссылкой удалится и его нельзя будет увидеть администраторам через сообщения группы)'
        h = sha1(bot.salt.encode() + str(bot.user.vk_id).encode()).hexdigest()[:-2]
        return {'message': answer,
                'keyboard': Keyboard.open_link('редактировать напоминания',
                                               f'https://vkbotkpv.loca.lt/settings?id={bot.user.vk_id}&h={h}')}, True
