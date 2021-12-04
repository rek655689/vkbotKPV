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


class User(Bot):
    """Любой пользователь, пнувший бота"""

    def __init__(self, db, vk_id: int, app):
        """db: объект базы данных
        vk_id: айди в вк
        member: является ли пользователь участником группы
        accept: ф-ция принятия в группу
        managers: список всех руководителей группы
        editors: список руководителей с должностью редактора
        is_manager: является ли пользователей руководителем"""

        super().__init__(app)
        self.db = db
        self.vk_id: int = vk_id
        self.member: bool = self.vk.groups.isMember(group_id=app.config['GROUP_ID'], user_id=vk_id)
        self.accept = accept(self.vk_id, self.vk_admin, app.config['GROUP_ID'])
        self.managers, self.editors = get_editors(self.vk, self.vk_admin, app.config['GROUP_ID'])
        self.is_manager = lambda x: True if self.vk_id in self.managers else False

        if self.member:
            in_db = db.users(vk_id, 'get', 'all')
            self.vk_name = in_db[1]
            self.id = in_db[2]
            self.name = in_db[3]

    def get_info(self, id: int) -> str or list:
        """Получение имени и должности игрока со страницы в CatWar"""
        profile = self.catwar_session.get(f'https://catwar.su/cat{id}').content.decode("utf-8")
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
