from settings import *


def get(vk):
    managers = []
    all = []
    for user in vk.groups.getMembers(group_id=group_id, filter='managers', access_token=access_token)['items']:
        if user.get('role') == 'editor':
            managers.append(user.get('id'))
            all.append(user.get('id'))
        else:
            all.append(user.get('id'))
    return all, managers


def last_manager(vk):
    mgs = get(vk)[1]
    times = {}

    for manager in mgs:
        last_seen = vk.users.get(user_ids=manager, fields='last_seen')[0].get('last_seen').get('time')
        times.update({last_seen: manager})

    m = max(times)
    return times.get(m)

