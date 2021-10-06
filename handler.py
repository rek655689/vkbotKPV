import commands
import introduction
from settings import *


def answer(vk, config, object):
    user_id = object.message['from_id']
    text = object.message['text'].lower()

    if 1 == commands.isMember(vk, token=token, group_id=group_id, user_id=user_id):
        if user_id == editor:
            if text in commands.editor_commands.keys():
                command = commands.editor_commands.get(text)
                commands.accept(vk, config, object)
            if text[0:18] == 'добавить в таблицу':
                commands.req(vk, config, object)

        table = commands.check_in_table(vk, config, object)
        if table:
            if table == 'create_reminder':
                commands.create_reminder(vk, config, object)
            elif table == 'del_reminders':
                commands.del_reminder(vk, config, object)
        elif text in commands.user_commands.keys():
                command = commands.user_commands.get(text)
                command(vk, config, object)
        else:
            commands.start(vk, config, object)
    else:
        introduction.intr(vk, config, object)