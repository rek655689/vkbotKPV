import commands


def answer(vk, settings, longpoll, config, object):
    if 1 == commands.isMember(vk, token=settings['token'], group_id=settings['group_id'], user_id=object.message['from_id']):
        if (object.message['text']).lower() == 'начать':
            commands.start(vk, longpoll, config, object)
        else:
            commands.dont_know(vk, config, object)

    else:
        commands.intr(vk, longpoll, config, object)