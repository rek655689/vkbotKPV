import commands


def answer(vk, settings, longpoll, config, object):
    if commands.isMember(vk, token=settings['token'], group_id=settings['group_id'], user_id=object.message['from_id']) == 1:
        if (object.message['text']).lower() == 'начать':
            commands.start(vk, longpoll, config, object)

    #else:

