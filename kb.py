from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def kb_exit():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Выйти', color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()


def kb_introduction():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Вступить', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Выйти', color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()


def kb_intr_req():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Готово', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Выйти', color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()


def kb_position():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Будущий Страж', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Будущий Охотник', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('Страж', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Охотник', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('Переходящий', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Котёнок', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('Выйти', color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()


def kb_request():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Принять', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Отклонить', color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()


def kb_start(perm):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Создать напоминание', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Мои напоминания', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Удалить напоминания', color=VkKeyboardColor.NEGATIVE)
    if perm:
        keyboard.add_line()
        keyboard.add_button('Заявки', color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()


def kb_action(times):
    keyboard = VkKeyboard(one_time=True)
    for i in times:
        keyboard.add_button(i, color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()


def kb_del():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Одно', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Все', color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()