from kb import Keyboard
from functools import wraps
import commands
import json


def pre_processing(func):
    @wraps(func)
    def inner(cls, message, bot):
        result, to_delete = func(cls, message, bot)

        # проверяем наличие кнопок у пользователя, если их нет, то пишем содержимое клавиатуры текстом
        if result.get('keyboard') and bot.user.keyboard is False:
            buttons = json.loads(result.get('keyboard'))['buttons'][0]
            message = result.get('message') + '\n Кнопки: '
            for b in buttons:
                try:
                    message += f'"{b["action"]["link"]}", '
                except KeyError:
                    message += f'"{b["action"]["label"]}", '
            del result['keyboard']
            result.update({'message': message[:-2]})

        # проверяем нужно ли удалить предыдущее сообщение
        message_id = bot.db.get_one('sent_messages', 'user_id', bot.user.vk_id, 'message_id')
        if message_id:
            bot.delete(message_id[0])

        return result, to_delete

    return inner


class CommandHandler:

    @classmethod
    @pre_processing
    def response(cls, message: dict, bot: object) -> dict and bool:

        # TODO: если не в группе, то intr

        # если пользователь уже запустил какую-то команду, то перенаправляем в неё
        run = bot.db.get_one('users', 'vk_id', bot.user.vk_id, 'command')[0]
        if run is not None:
            for command in commands.Command.__subclasses__():
                if run in command.name:
                    return command.run(bot, message)
        else:
            # поиск нужной команды
            text = message['text'].lower()
            for command in commands.Command.__subclasses__():
                if text in command.name:
                    if bot.user.role not in command.access:
                        return {'message': 'К сожалению, доступ к команде закрыт :(\n'
                                           'Обратись к руководству группы, чтобы его получить'}, False
                    else:
                        return command.run(bot, message)
            else:
                return {'message': 'Команда не найдена. Напиши "помощь", чтобы узнать больше',
                        'keyboard': Keyboard.buttons({'помощь': 'SECONDARY'})}, False
