from vk_api.utils import get_random_id
import kb
from vk_api.bot_longpoll import VkBotEventType

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

    def process(self):
        pass


def add_patr(vk, longpoll, config, object):
    vk.messages.send(**config, random_id=get_random_id(), user_id=object.message['from_id'],
                     message='Выбери время:',
                     keyboard=kb.kb_patr(patr.times),
                     )
    event = longpoll.check()[-1]
    while event.type != VkBotEventType.MESSAGE_NEW:
        event = list(longpoll.check())
        event = event[-1]
            #(object.message['text']).lower() в бд
    add_time = event.object.message['text']
    vk.messages.send(**config, random_id=get_random_id(), user_id=object.message['from_id'],
                             message='Патруль в ' + add_time + ' успешно добавлен',
                             )


patr = Actions()
patr.vars = ['патруль', 'патрули', 'патр', 'патры', 'пп']
patr.times = ['12:00', '13:00']
patr.process = add_patr