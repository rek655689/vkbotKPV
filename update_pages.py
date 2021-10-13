from settings import *
import vk_api
import connection
import requests
import re
import pandas as pd
import csv
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import time
from vk_api.utils import get_random_id

seconds = time.time()
local_time = time.ctime(seconds)

vk, longpoll, config = connection.connect(vk_api, requests, time, local_time)
vk_token = (vk_api.VkApi(token=access_token)).get_api()
# vk_token - токен пользователя-админа для работы с админскими правами


url = 'https://catwar.su/ajax/login'
user_agent_val = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/90.0.4430.93 Safari/537.36 '
session = HTMLSession()
session.headers.update({'Referer': url})
session.headers.update({'User-Agent': user_agent_val})
session.post(url, {**catwar})

future_guards = ('будущий страж', 'будущая стражница')
future_hunters = ('будущий охотник', 'будущая охотница')
hunters = ('охотник', 'охотница')
guards = ('страж', 'стражница')
elders = ('старейшина',)
others = ('котёнок', 'переходящий', 'переходящая', 'разрешение')
elects = ('избранник духов', 'избранница духов')
top = ('врачеватель', 'врачевательница', 'ученик врачевателя', 'ученица врачевателя', 'советник', 'советница')

positions = {'elects': elects, 'top': top, 'elders': elders, 'hunters': hunters, 'guards': guards,
             'future_guards': future_guards, 'future_hunters': future_hunters, 'others': others}

for_page = {'elders': 'старейшины!конец старейшины', 'guards 1': 'стражи!конец стражи', 'guards 2': 'стражи2!конец стражи2',
            'hunters 1': 'охотники!конц охотники', 'hunters 2': 'охотники2!конец охотники 2',
            'future_guards': 'будущие с! конец с', 'future_hunters': 'бдущие о! конец о',
            'top': 'начало верх!конец верх', 'elects': 'избранники!конец',
            'others': "<center>[[photo350643392_457280584|51x66px;nopadding|page-165101106_55801160]][[photo350643392_457280585|86x66px;nopadding|page-165101106_55801147]][[photo350643392_457280616|73x66px;nopadding|page-165101106_56886361]][[photo350643392_457280587|76x66px;nopadding|page-165101106_56461101]][[photo350643392_457280588|68x66px;nopadding|page-165101106_56886994]][[photo350643392_457280589|66x66px;nopadding|https://vk.com/wall-165101106_2060]][[photo350643392_457280590|90x66px;nopadding|https://docs.google.com/forms/d/e/1FAIpQLSfPSd7DbT7oaIVEagDtZiS8FUd5PkWz9d0G9vuK4qPMhbl4Sg/viewform]]</center>\n<center>[[page-165101106_56490990|Верхушка]] | '''[[page-165101106_56591896|Старейшины]]''' | [[page-165101106_56846221|Избранники духов]]\n[[page-165101106_56807806|Стражи]] | [[page-165101106_56807807|Охотники]] | [[page-165101106_56490171|Будущие]]\n[[page-165101106_56808867|Прочие игроки]]</center>\n!конец"}

# пирожок
page_ids = {'elders': 56444175, 'guards 1': 56444151, 'guards 2': 56444152, 'hunters 1': 56444681, 'hunters 2': 56444732,
            'future_guards': 56444735, 'future_hunters': 56444736, 'top': 56445284, 'elects': 56445285, 'others': 56445286}

max_row = 85


def get_key(d, value):
    for k, v in d.items():
        for x in v:
            if x == value:
                return k


def get_members():
    """Перенос таблиц из wiki-страниц в csv"""
    with open('table.csv', mode="w", encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=",", lineterminator="\r")
        writer.writerow(['vk_id', 'vk_name', 'name', 'id', 'position'])

        for page_id in page_ids.values():
            orig_page = vk_token.pages.get(**config, owner_id=-group_id, page_id=page_id, need_source=1)['source']
            start = orig_page.find('{|') + 3
            end = orig_page.find('|}')
            page = orig_page[start:end]

            c = 0
            i = 0
            lens = len(page)

            while i < lens:
                if c < 3:
                    start = page.find('\n', i)
                    end = page.find('\n', start + 1)
                    s = page[start:end]
                    i = end

                    if c == 0:
                        vk_id = re.findall("[0-9]+", s)[0]
                        vk_name = re.findall("\|[^0-9\]\]\[]+", s)[1][1:]

                    if c == 1:
                        name = re.findall("\[[^0-9\]\]\[]+", s)[0][1:-1]
                        id = re.findall("[0-9]+", s)[0]

                    if c == 3:
                        pass

                    c += 1
                else:
                    c = 0
                    i += 3
                    try:
                        position = BeautifulSoup(session.get(f'https://catwar.su/cat{id}').content.decode("utf-8"), 'html.parser').find('i').text
                    except AttributeError:
                        continue
                    writer.writerow([vk_id, vk_name, name, id, position])
                    print(vk_id, vk_name, name, id, position)


def check_members():
    """Проверка игроков в таблице на нахождение в клане, правильность должности/имени/имени в ВК"""

    df = pd.read_csv('table.csv')

    for row in df.itertuples(index=True, name=None):
        index, vk_id, vk_name, name, id, position = row[0], row[1], row[2], row[3], row[4], row[5]
        print(index, vk_id, vk_name, name, id, position)

        profile = session.get(f'https://catwar.su/cat{id}').content.decode("utf-8")
        try:
            # если нет должности, значит чел не в клане
            real_position = BeautifulSoup(profile, 'html.parser').find('i').text.lower()
        except AttributeError:
            real_position = None

        try:
            # если нет имени , значит чел не в клане
            cw_name = BeautifulSoup(profile, 'html.parser').find('big').text
        except AttributeError:
            cw_name = None

        # if (vk.groups.isMember(group_id=group_id, user_id=vk_id) == 0) or position is None or cw_name is None:
        if (real_position is None and position != 'разрешение') or cw_name is None:
            # если чел не в клане - убираем из таблицы
            df = df.drop(index)
            print(f'\n{vk_id} удалён')
            if vk.groups.isMember(group_id=group_id, user_id=vk_id) == 1:
                # если чел при этом участник группы - кикаем
                vk_token.groups.removeUser(group_id=group_id, user_id=vk_id)
            continue

        real_vk_name = vk.users.get(user_ids=vk_id, fields='first_name, last_name')[0]
        real_vk_name = real_vk_name['first_name'] + ' ' + real_vk_name['last_name']

        if real_vk_name != vk_name:
            df.loc[index, 'vk_name'] = real_vk_name

        if cw_name != name:
            df.loc[index, 'name'] = cw_name

        if real_position != position:
            if position != 'разрешение':
                df.loc[index, 'position'] = real_position

        if real_position is not None and get_key(positions, real_position) is None:
            # если должность существует, но у нас таких нет, удаляем
            df = df.drop(index)
            print(f'\n{vk_id} удалён')
            continue
    df = df.drop_duplicates()
    df.to_csv('table.csv', index=False)


def add_member(vk_id, vk_name, name, id, position):
    """Добавление в csv"""
    with open('table.csv', mode="a", encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=",", lineterminator="\n")
        writer.writerow([vk_id, vk_name.title(), name.title(), id, position])


def edit_member(user_id):
    """Изменить должность в csv"""
    df = pd.read_csv('table.csv')
    i = len((df.loc[df['id'] == user_id]).index)
    while i > 0:
        for row in df.itertuples(index=True, name=None):
            index, id = row[0], row[4]
            if id == user_id:
                df.loc[index, 'position'] = 'разрешение'
                i -= 1
    df.to_csv('table.csv', index=False)


def add_to_page():
    """Перенос из таблицы excel на wiki-страницы"""
    df = pd.read_csv('table.csv')
    df = df.drop_duplicates()

    for key, value in positions.items():
        rows = df.loc[df['position'].isin(value)]
        rows = rows.sort_values('name')

        if key == 'guards' or key == 'hunters':
            key1 = key + ' 1'
            key2 = key + ' 2'
            rows1 = rows.iloc[0:max_row]
            rows2 = rows.iloc[max_row:len(rows.index)+1]
            start1, end1 = for_page.get(key1).split('!')
            start2, end2 = for_page.get(key2).split('!')
            text = start1 + '\n{|\n'

            for row in rows1.itertuples(index=True, name=None):
                index, vk_id, vk_name, name, id, position = row[0], row[1], row[2], row[3], row[4], row[5]
                print(index, vk_id, vk_name, name, id, position)
                text += f'|-\n| [[id{vk_id}|{vk_name}]]\n| [{name}|{id}]\n| [https://catwar.su/cat{id}]\n'

            text += '|}\n' + end1
            page_id = page_ids.get(key1)
            vk_token.pages.save(text=text, page_id=page_id, group_id=group_id)

            text = start2 + '\n{|\n'

            for row in rows2.itertuples(index=True, name=None):
                index, vk_id, vk_name, name, id, position = row[0], row[1], row[2], row[3], row[4], row[5]
                print(index, vk_id, vk_name, name, id, position)
                text += f'|-\n| [[id{vk_id}|{vk_name}]]\n| [{name}|{id}]\n| [https://catwar.su/cat{id}]\n'

            text += '|}\n' + end2
            page_id = page_ids.get(key2)
            vk_token.pages.save(text=text, page_id=page_id, group_id=group_id)

        elif key == 'top':
            start, end = for_page.get(key).split('!')
            text = start + '\n'

            row = list(rows.loc[df['position'].isin(('врачеватель', 'врачевательница'))].itertuples(index=True, name=None))[0]
            index, vk_id, vk_name, name, id, position = row[0], row[1], row[2], row[3], row[4], row[5]
            text += f"<center>'''{position.capitalize()}'''</center>" + '\n{|\n'
            text += f'|-\n| [[id{vk_id}|{vk_name}]]\n| [{name}|{id}]\n| [https://catwar.su/cat{id}]\n'
            text += '|}\n'

            try:
                row = list(rows.loc[df['position'].isin(('ученик врачевателя', 'ученица врачевателя'))].itertuples(index=True, name=None))[0]
                index, vk_id, vk_name, name, id, position = row[0], row[1], row[2], row[3], row[4], row[5]
                text += f"<center>'''{position.capitalize()}'''</center>" + '\n{|\n'
                text += f'|-\n| [[id{vk_id}|{vk_name}]]\n| [{name}|{id}]\n| [https://catwar.su/cat{id}]\n'
                text += '|}\n'
            except IndexError:
                text += "<center>'''Ученик врачевателя'''</center>\n{|\n—\n|}\n"

            text += "<center>'''Советники'''</center>" + '\n{|\n'
            try:
                rows1 = rows.loc[df['position'].isin(('советник', 'советница'))]
                for row in rows1.itertuples(index=True, name=None):
                    index, vk_id, vk_name, name, id, position = row[0], row[1], row[2], row[3], row[4], row[5]
                    print(index, vk_id, vk_name, name, id, position)
                    text += f'|-\n| [[id{vk_id}|{vk_name}]]\n| [{name}|{id}]\n| [https://catwar.su/cat{id}]\n'
            except IndexError:
                text += "—\n"
            text += '|}\n' + end

            page_id = page_ids.get(key)
            vk_token.pages.save(text=text, page_id=page_id, group_id=group_id)

        elif key == 'elects':
            start, end = for_page.get(key).split('!')
            text = start + '\n'
            ivolga = "<center>'''Избранники Иволги'''</center>\n{|\n"
            lisa = "<center>'''Избранники Лисы'''</center>\n{|\n"
            laska = "<center>'''Избранники Ласки'''</center>\n{|\n"
            img_ivolga = ('<img border="0" src="http://images.vfl.ru/ii/1604159092/1dda3f82/32141463.png"/>',
                          '<img border="0" src="http://images.vfl.ru/ii/1615720730/9aab1182/33672466.gif"/>')
            img_lisa = ('<img border="0" src="http://images.vfl.ru/ii/1604159092/448b5ed6/32141465.png"/>',
                        '<img border="0" src="https://s6.gifyu.com/images/AKTIVISTLISOV.gif"/>')
            img_laska = ('<img border="0" src="http://images.vfl.ru/ii/1604159092/ed9c5fbd/32141464.png"/>',
                         '<img border="0" src="http://images.vfl.ru/ii/1612281558/f02c85e9/33190772.gif"/>')

            for row in rows.itertuples(index=True, name=None):
                index, vk_id, vk_name, name, id, position = row[0], row[1], row[2], row[3], row[4], row[5]
                profile = session.get(f'https://catwar.su/cat{id}').content.decode("utf-8")
                elect = BeautifulSoup(profile, 'html.parser').find_all(border='0')
                for img in elect:
                    img = str(img)
                    if img in img_ivolga:
                        ivolga += f'|-\n| [[id{vk_id}|{vk_name}]]\n| [{name}|{id}]\n| [https://catwar.su/cat{id}]\n'
                        break
                    elif img in img_laska:
                        laska += f'|-\n| [[id{vk_id}|{vk_name}]]\n| [{name}|{id}]\n| [https://catwar.su/cat{id}]\n'
                        break
                    elif img in img_lisa:
                        lisa += f'|-\n| [[id{vk_id}|{vk_name}]]\n| [{name}|{id}]\n| [https://catwar.su/cat{id}]\n'
                        break
                else:
                    print(f'\n{elect} не найден')
                print(index, vk_id, vk_name, name, id, position)
            text += ivolga + '|}\n' + lisa + '|}\n' + laska + '|}\n' + end

            page_id = page_ids.get(key)
            vk_token.pages.save(text=text, page_id=page_id, group_id=group_id)

        elif key == 'others':
            start, end = for_page.get(key).split('!')
            text = start + '\n'

            rows1 = rows.loc[df['position'].isin(('котёнок',))]
            text += "<center>'''Котята'''</center>\n{|\n"
            try:
                for row in rows1.itertuples(index=True, name=None):
                    index, vk_id, vk_name, name, id, position = row[0], row[1], row[2], row[3], row[4], row[5]
                    text += f'|-\n| [[id{vk_id}|{vk_name}]]\n| [{name}|{id}]\n| [https://catwar.su/cat{id}]\n'
                    print(index, vk_id, vk_name, name, id, position)
            except IndexError:
                text += '—\n'
            text += '|}\n'

            rows2 = rows.loc[df['position'].isin(('переходящий', 'переходящая'))]
            text += "<center>'''Переходящие'''</center>\n{|\n"
            try:
                for row in rows2.itertuples(index=True, name=None):
                    index, vk_id, vk_name, name, id, position = row[0], row[1], row[2], row[3], row[4], row[5]
                    text += f'|-\n| [[id{vk_id}|{vk_name}]]\n| [{name}|{id}]\n| [https://catwar.su/cat{id}]\n'
                    print(index, vk_id, vk_name, name, id, position)
            except IndexError:
                text += '—\n'
            text += '|}\n'

            rows3 = rows.loc[df['position'].isin(('разрешение',))]
            text += "<center>'''С разрешением на нахождение в группе'''</center>\n{|\n"
            try:
                for row in rows3.itertuples(index=True, name=None):
                    index, vk_id, vk_name, name, id, position = row[0], row[1], row[2], row[3], row[4], row[5]
                    text += f'|-\n| [[id{vk_id}|{vk_name}]]\n| [{name}|{id}]\n| [https://catwar.su/cat{id}]\n'
                    print(index, vk_id, vk_name, name, id, position)
            except IndexError:
                text += '—\n'
            text += '|}\n' + end

            page_id = page_ids.get(key)
            vk_token.pages.save(text=text, page_id=page_id, group_id=group_id)

        else:
            start, end = for_page.get(key).split('!')
            text = start + '\n{|\n'

            for row in rows.itertuples(index=True, name=None):
                index, vk_id, vk_name, name, id, position = row[0], row[1], row[2], row[3], row[4], row[5]
                print(index, vk_id, vk_name, name, id, position)
                text += f'|-\n| [[id{vk_id}|{vk_name}]]\n| [{name}|{id}]\n| [https://catwar.su/cat{id}]\n'

            text += '|}\n' + end

            page_id = page_ids.get(key)
            vk_token.pages.save(text=text, page_id=page_id, group_id=group_id)
