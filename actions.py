from vk_api.utils import get_random_id
import database

action_list = []
other_actions = []


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

    def send10(self, vk, config, times, action):
        ids = list()
        result = database.check_ids(self.vars[0], times, 10)
        for x in result:
            ids.append(x[0])
        name = action.vars[0]
        if ids:
            vk.messages.send(**config, random_id=get_random_id(), peer_ids=ids,
                             message=f'Через 10 минут будет {name}'
                             )

    def send5(self, vk, config, times, action):
        ids = list()
        result = database.check_ids(self.vars[0], times, 5)
        for x in result:
            ids.append(x[0])
        name = action.vars[0]
        if ids:
            vk.messages.send(**config, random_id=get_random_id(), peer_ids=ids,
                             message=f'Через 5 минут будет {name}'
                             )

    def get_var_name(self):
        for k, v in globals().items():
            if v is self:
                return k

    def __str__(self):
        return {self.get_var_name()}


patr = Actions()
patr.vars = ['пограничный патруль', 'патруль', 'патрули', 'патр', 'патры', 'пп']
patr.times = ['10:20', '13:00', '15:00', '18:20', '20:00']

hunt = Actions()
hunt.vars = ['охотничий патруль', 'охота', 'охоты', 'оп']
hunt.times = ['11:20', '13:20', '14:20', '16:20', '19:00']

swim = Actions()
swim.vars = ['заплыв', 'плыв', 'заплывы']
swim.times = ['12:00', '21:00']

mass = Actions()
mass.vars = ['массовая тренировка', 'массовка', 'масовка', 'массокач', 'масокач', 'маскач']
mass.times = ['15:10', '17:20']

grass = Actions()
grass.vars = ['травник', 'трав', 'сбор трав']
grass.times = ['16:00']

moss = Actions()
moss.vars = ['сбор мха', 'мох', 'мохосбор']
moss.times = ['17:00']

web = Actions()
web.vars = ['сбор паутины', 'паутина', 'пау', 'паусбор']
web.times = ['16:00']

meeting = Actions()
meeting.vars = ['собрание', 'собр', 'собрание', 'собра']
meeting.times = ['16:00', '18:00', '19:00']
other_actions.append(meeting)

branches = Actions()
branches.vars = ['сбор веток', 'ветки', 'крепкие ветки', 'вьюнки']
branches.times = ['12:00', '16:00']

brightest_night = Actions()
brightest_night.vars = ['самая яркая ночь', 'сян', 'самая-яркая-ночь']
brightest_night.times = ['18:00']
other_actions.append(brightest_night)