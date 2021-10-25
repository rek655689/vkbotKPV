import commands
import managers
import introduction
from settings import *


def answer(vk, config, object):
    manage = managers.get(vk)[0]

    user_id = object.message['from_id']
    text = object.message['text'].lower()

    if 1 == vk.groups.isMember(access_token=token, user_id=user_id, group_id=group_id):
        if user_id == editor or user_id in manage:
            if text[0:7] == 'принять':
                commands.accept(vk, config, object)
            if text[0:9] == 'отклонить':
                commands.reject(vk, config, object)
            if text[0:18] == 'добавить в таблицу':
                commands.req(vk, config, object)
            if text[0:17] == 'оставить в группе':
                commands.edit_position(vk, config, object)

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