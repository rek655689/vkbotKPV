from vk_api.utils import get_random_id
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

    def send(self, vk, config, time):
        ids = database.check_ids(self.vars[0], time)[0]
        vk.messages.send(**config, random_id=get_random_id(), peer_ids=ids,
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
patr.times = ['10:20', '13:00', '15:00', '18:20', '20:00']

hunt = Actions()
hunt.vars = ['охота', 'охоты', 'оп']
hunt.times = ['11:20', '13:20', '14:20', '16:20', '19:00']

swim = Actions()
swim.vars = ['заплыв', 'плыв', 'заплывы']
swim.times = ['12:00', '21:00']

mass = Actions()
mass.vars = ['массовая тренировка', 'массовка', 'массокач', 'маскач']
mass.times = ['12:00', '17:20']

grass = Actions()
grass.vars = ['травник', 'трав', 'сбор трав']
grass.times = ['16:00']

moss = Actions()
moss.vars = ['мох', 'мохосбор', 'сбор мха']
moss.times = ['16:00']