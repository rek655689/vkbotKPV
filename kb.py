from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def kb_start():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Создать напоминание', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Мои напоминания', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Удалить напоминание', color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()


def kb_patr(times):
    keyboard = VkKeyboard(one_time=True)
    for i in times:
        keyboard.add_button(i, color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()