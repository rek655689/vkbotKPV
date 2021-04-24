import commands
import introduction
import yaml

with open('/settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)
    editor = settings['editor']


def answer(vk, settings, config, object):
    user_id = object.message['from_id']

    if 1 == commands.isMember(vk, token=settings['token'], group_id=settings['group_id'], user_id=user_id):
        if user_id == editor:
            if object.message['text'].lower() == 'принять' or object.message['text'].lower() == 'отклонить':
                commands.editor_answer(vk, settings, config, object)
            if object.message['text'].lower() == 'заявки':
                commands.req(vk, config, object)

        table = commands.check_in_table(user_id)
        if table:
            if table == 'create_reminder':
                commands.create_reminder(vk, config, object)
            elif table == 'del_reminders':
                commands.del_reminder(vk, config, object)
        elif object.message['text'].lower() == 'создать напоминание':
            commands.create_reminder(vk, config, object)
        elif object.message['text'].lower() == 'мои напоминания':
            commands.show_reminders(vk, config, object)
        elif object.message['text'].lower() == 'удалить напоминания':
            commands.del_reminder(vk, config, object)
        else:
            commands.start(vk, config, object)
    else:
        introduction.intr(vk, config, object)