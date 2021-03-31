from vk_api.utils import get_random_id
import kb
from vk_api.bot_longpoll import VkBotEventType
import database

action_list = []


class Actions:
    def __init__(self):
        self.vars = []
        self.times = []
        action_list.append(self)

    @property
    def vars(self):
        return self.vars

    def times(self):
        return self.times

    def vars(self, var):
        for k in var:
            self.vars.append(k.lower())

    def times(self, time):
        for k in time:
            self.times.append(k.lower())

    def add(self, vk, longpoll, config, object):
        user_id = object.message['from_id']
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message='Выбери время:',
                         keyboard=kb.kb_action(self.times),
                         )
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.object.message['from_id'] == user_id:
                    event = event
                    break
        time = event.object.message['text']
        database.add_action(user_id=user_id, action=self.vars[0], time=time)
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message=(self.vars[0]).title() + ' в ' + time + ' успешно добавлен(а)',
                         )

    def delete(self, vk, longpoll, config, object):
        user_id = object.message['from_id']
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message='Выбери время:',
                         keyboard=kb.kb_action(self.times),
                         )
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.object.message['from_id'] == user_id:
                    event = event
                    break
        time = event.object.message['text']
        database.del_action(user_id=user_id, action=self.vars[0], time=time)
        vk.messages.send(**config, random_id=get_random_id(), user_id=user_id,
                         message=(self.vars[0]).title() + ' в ' + time + ' успешно удален(а)',
                         )

    def send(self, vk, config, time):
        ids = database.check_ids(self.vars[0], time)[0]
        vk.messages.send(**config, random_id=get_random_id(), peer_ids=(478936081, 597786732),
                         message=time + ' успешно'
                         )

    def get_var_name(self):
        for k, v in globals().items():
            if v is self:
                return k

    def __str__(self):
        return {self.get_var_name()}


patr = Actions()
patr.vars = ['патруль', 'патрули', 'патр', 'патры', 'пп']
patr.times = ['12:00', '13:00']

hunt = Actions()
hunt.vars = ['охота', 'охоты', 'оп']
hunt.times = ['10:00', '11:22']
