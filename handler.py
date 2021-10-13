import commands
import introduction
from settings import *

managers = []


def answer(vk, config, object):
    for user in vk.groups.getMembers(group_id=group_id, filter='managers', access_token=access_token)['items']:
        managers.append(user.get('id'))

    user_id = object.message['from_id']
    text = object.message['text'].lower()

    if 1 == vk.groups.isMember(access_token=token, user_id=user_id, group_id=group_id):
        if user_id == editor or user_id in managers:
            if text in commands.editor_commands.keys():
                command = commands.editor_commands.get(text)
                command(vk, config, object)
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