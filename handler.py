import commands
import introduction


def answer(vk, settings, config, object):
    editor = settings['editor']
    user_id = object.message['from_id']

    if 1 == commands.isMember(vk, token=settings['token'], group_id=settings['group_id'], user_id=user_id):
        if user_id == editor:
            if object.message['text'].lower() == 'принять' or object.message['text'].lower() == 'отклонить':
                commands.editor_answer(vk, settings, config, object)
            if object.message['text'].lower() == 'заявки':
                commands.req(vk, settings, config, object)

        table = commands.check_in_table(user_id)
        if table:
            if table == 'create_reminder':
                commands.create_reminder(vk, settings, config, object)
            elif table == 'del_reminders':
                commands.del_reminder(vk, settings, config, object)
        elif object.message['text'].lower() == 'создать напоминание':
            commands.create_reminder(vk, settings, config, object)
        elif object.message['text'].lower() == 'мои напоминания':
            commands.show_reminders(vk, settings, config, object)
        elif object.message['text'].lower() == 'удалить напоминания':
            commands.del_reminder(vk, settings, config, object)
        elif object.message['text'].lower() == 'таблица занятости':
            commands.table(vk, settings, config, object)
        elif object.message['text'].lower() == 'предложить идею':
            commands.table(vk, settings, config, object)
        else:
            commands.start(vk, settings, config, object)
    else:
        introduction.intr(vk, settings, config, object)