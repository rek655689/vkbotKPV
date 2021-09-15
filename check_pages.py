import re
import schedule
import time
import vk_api
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from vk_api.utils import get_random_id
import connection
from settings import *

seconds = time.time()
local_time = time.ctime(seconds)

vk, longpoll, config = connection.connect(vk_api, requests, time, local_time)
vk_token = (vk_api.VkApi(token=access_token)).get_api()


def check_pages(vk, config):
    # авторизация
    url = 'https://catwar.su/ajax/login'
    user_agent_val = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                     'Chrome/90.0.4430.93 Safari/537.36 '
    session = HTMLSession()
    session.headers.update({'Referer': url})
    session.headers.update({'User-Agent': user_agent_val})
    session.post(url, {**catwar})

    heads = ('врачеватель', 'врачевательница', 'ученик врачевателя', 'ученица врачевателя', 'советник', 'советница')
    elders = ('старейшина')
    elects = ('избранник духов', 'избранница духов')
    guards = ('страж', 'стражница')
    hunters = ('охотник', 'охотница')
    futures = ('будущий охотник', 'будущая охотница', 'будущий страж', 'будущая стражница')
    others = ('котёнок', 'переходящий', 'переходящая')
    page_ids = {heads: 56490990, elders: 56591896, elects: 56846221,  guards: 56807806,
                hunters: 56807807, futures: 56490171, others: 56808867}
    wrong_names, dels, not_position = [], [], []
    m_1, m_2, m_3 = '', '', ''

    for key, value in page_ids.items():
        # получаем данные со страницы
        orig_page = vk_token.pages.get(**config, owner_id=-group_id, page_id=value, need_source=1)
        orig_page = orig_page['source']
        page = orig_page[(orig_page.find("{|") + 2):(orig_page.find("|}"))]

        vk_ids = re.findall("id[0-9]+", page)
        i = 0
        while i < len(vk_ids):
            vk_ids[i] = vk_ids[i][2:]
            i += 1

        vk_names = re.findall("\|[^ -][^0-9\]\]\[]+", page)
        i = 0
        while i < len(vk_names):
            vk_names[i] = vk_names[i][1:]
            i += 1

        vk_dict = dict(zip(vk_ids, vk_names))

        ids = re.findall("\|[0-9]+", page)
        i = 0
        while i < len(ids):
            ids[i] = ids[i][1:]
            i += 1

        names = re.findall("\[[А-яё ]+", page)
        i = 0
        while i < len(names):
            names[i] = names[i][1:]
            i += 1

        # проверка вкшных имён
        for vk_key, vk_value in vk_dict.items():
            vk_name = vk.users.get(user_ids=vk_key, fields='first_name, last_name')[0]
            vk_name = vk_name['first_name'] + ' ' + vk_name['last_name']
            if vk_value != vk_name:
                wrong_names.append(f'{vk_value} — {vk_name}')

        # проверка на нахождение в клане и должности
        for id in ids:
            response = session.get(f'https://catwar.su/cat{id}')
            profile = response.content.decode("utf-8")
            soup = BeautifulSoup(profile, 'html.parser')
            position = soup.find('i')
            if not position:
                if id != 539719 or id != 1068731:
                    dels.append(f'{key[0]} — {id}')
            else:
                position = position.text
                position = re.match('[^i<>/]+', position).group()
                if position.lower() not in key:
                    not_position.append(f'{id} не {key[0]}, a {position}')

    for x in dels:
        m_1 = m_1 + x + '\n'
    for x in not_position:
        m_2 = m_2 + x + '\n'
    for x in wrong_names:
        m_3 = m_3 + x + '\n'

    vk.messages.send(**config, random_id=get_random_id(), user_id=editor,
                     message=f'Удалены или не в клане: {m_1}\n\n'
                     )
    vk.messages.send(**config, random_id=get_random_id(), user_id=editor,
                     message=f'Другие должности: {m_2}\n\n'
                     )
    vk.messages.send(**config, random_id=get_random_id(), user_id=editor,
                     message=f'Другие имена: {m_3}\n\n',
                     )


schedule.every().day.at('20:00').do(check_pages, vk, config)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write('\nPages: '+local_time+' '+str(e) + '\n')
        continue
