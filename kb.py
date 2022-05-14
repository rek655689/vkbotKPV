from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json


class Keyboard:
    """Варианты клавиатуры

    inline: кнопки в сообщении
    one_time: кнопки исчезают после отправки сообщения"""

    @staticmethod
    def exit() -> str:
        keyboard = VkKeyboard(inline=True)
        keyboard.add_button('Выйти', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    @staticmethod
    def menu() -> str:
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Создать напоминание', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Мои напоминания', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Удалить напоминания', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Таблица занятости', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('Предложить идею', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()

    @staticmethod
    def buttons(d: dict) -> str:
        keyboard = VkKeyboard(inline=True)
        for text, color in d.items():
            keyboard.add_callback_button(text, color=eval(f'VkKeyboardColor.{color}'), payload={'text': text})
        return keyboard.get_keyboard()

    @staticmethod
    def open_link(text: str, link: str) -> str:
        keyboard = VkKeyboard(inline=True)
        keyboard.add_openlink_button(text, link, payload={'text': text})
        return keyboard.get_keyboard()

    @staticmethod
    def anket() -> str:
        keyboard = VkKeyboard(inline=True)
        keyboard.add_callback_button('Да', color=VkKeyboardColor.POSITIVE)
        keyboard.add_callback_button('Нет', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    @staticmethod
    def request(user_id) -> str:
        keyboard = VkKeyboard(inline=True)
        keyboard.add_button(f'Принять {user_id}', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(f'Отклонить {user_id}', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()


# def kb_introduction():
#     keyboard = VkKeyboard(one_time=True)
#     keyboard.add_button('Вступить', color=VkKeyboardColor.POSITIVE)
#     keyboard.add_button('Выйти', color=VkKeyboardColor.NEGATIVE)
#     return keyboard.get_keyboard()
#
#
# def kb_intr_req():
#     keyboard = VkKeyboard(one_time=True)
#     keyboard.add_button('Готово', color=VkKeyboardColor.POSITIVE)
#     keyboard.add_button('Выйти', color=VkKeyboardColor.NEGATIVE)
#     return keyboard.get_keyboard()
#
#
# def kb_position():
#     keyboard = VkKeyboard(inline=True)
#     keyboard.add_button('Будущий Страж', color=VkKeyboardColor.SECONDARY)
#     keyboard.add_button('Будущий Охотник', color=VkKeyboardColor.SECONDARY)
#     keyboard.add_line()
#     keyboard.add_button('Страж', color=VkKeyboardColor.SECONDARY)
#     keyboard.add_button('Охотник', color=VkKeyboardColor.SECONDARY)
#     keyboard.add_line()
#     keyboard.add_button('Переходящий', color=VkKeyboardColor.SECONDARY)
#     keyboard.add_button('Котёнок', color=VkKeyboardColor.SECONDARY)
#     keyboard.add_line()
#     keyboard.add_button('Выйти', color=VkKeyboardColor.NEGATIVE)
#     return keyboard.get_keyboard()
#
#
# def kb_start():
#
#
#
# def kb_action(times):
#     keyboard = VkKeyboard(inline=True)
#     for i in times:
#         keyboard.add_button(i, color=VkKeyboardColor.SECONDARY)
#         keyboard.add_line()
#     keyboard.add_button('Выйти', color=VkKeyboardColor.NEGATIVE)
#     return keyboard.get_keyboard()
#
#
# def kb_section():
#     keyboard = VkKeyboard(inline=True)
#     keyboard.add_button('5', color=VkKeyboardColor.SECONDARY)
#     keyboard.add_button('10', color=VkKeyboardColor.SECONDARY)
#     return keyboard.get_keyboard()
#
#
# def kb_del():
#     keyboard = VkKeyboard(inline=True)
#     keyboard.add_button('Одно', color=VkKeyboardColor.SECONDARY)
#     keyboard.add_button('Все', color=VkKeyboardColor.SECONDARY)
#     keyboard.add_button('Выйти', color=VkKeyboardColor.NEGATIVE)
#     return keyboard.get_keyboard()