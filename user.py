from bot import Bot
from bs4 import BeautifulSoup
from vk_api.exceptions import ApiError


def accept(vk_id: int, vk_admin: any, group_id: int) -> bool:
    """Принятие в группу"""
    try:
        vk_admin.groups.approveRequest(group_id=group_id, user_id=vk_id)
        return True
    except ApiError:
        return False


def get_editors(vk: any, access_token: any, group_id: int) -> tuple:
    """Получение списка пользователей, являющихся руководителями группы (managers)
    и отдельно только редакторов (editors)"""
    managers = []
    all = []
    for user in vk.groups.getMembers(group_id=group_id, filter='managers', access_token=access_token)['items']:
        if user.get('role') == 'editor' or user.get('role') == 'creator':
            managers.append(user.get('id'))
            all.append(user.get('id'))
        else:
            all.append(user.get('id'))
    return all, managers


def get_role(vk_id: int, vk_admin, group_id) -> str:
    managers = vk_admin.groups.getMembers(group_id=group_id, filter='managers')['items']
    for user in managers:
        if user.get('id') == vk_id:
            return user.get('role')
    else:
        return 'user'


class User:

    def __init__(self, data, group_id: int, bot):
        """
        :param data: объект события или сообщения
        :param group_id: ID группы
        :param bot: объект бота
        """

        # ID пользователя
        self.vk_id: int = data['object']['message']['from_id'] if data['type'] == 'message_new' else data['object']['user_id']

        # является ли пользователь участником группы
        self.member: bool = bot.vk.groups.isMember(group_id=group_id, user_id=self.vk_id)

        # роль пользователя в группе
        self.role = None
        if self.member:
            self.role = get_role(self.vk_id, bot.vk_admin, group_id)

        # доступна ли клавиатура
        self.keyboard: bool = data['object']['client_info']['inline_keyboard'] if data['type'] == 'message_new' else None

    def get_info(self, id: int, bot) -> str or list:
        """Получение имени и должности игрока со страницы в CatWar"""
        profile = bot.catwar_session.get(f'https://catwar.su/cat{id}').content.decode("utf-8")
        try:
            name = BeautifulSoup(profile, 'html.parser').find('big').text.title()
        except AttributeError:
            return 'нет имени'
        try:
            position = BeautifulSoup(profile, 'html.parser').find('i').text.lower()
        except AttributeError:
            return 'нет должности'
        return [name, position]

    def last_editor(self) -> int:
        """Получение последнего заходившего в ВК редактора"""
        if not self.editors:
            "Если в группе нет редакторов, их роль будут выполнять другие остальные руководители"
            editors = self.managers
        else:
            editors = self.editors

        times = {}

        for editor in editors:
            last_seen = self.vk.users.get(user_ids=editor, fields='last_seen')[0].get('last_seen').get('time')
            times.update({last_seen: editor})

        m = max(times)
        return times.get(m)
