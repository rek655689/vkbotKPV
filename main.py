import requests
import time
import vk_api
from vk_api.bot_longpoll import VkBotEventType
import connection
import handler

seconds = time.time()
local_time = time.ctime(seconds)


vk, longpoll, config = connection.connect(vk_api, requests, time, local_time)

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
                handler.answer(vk, config, event.object)
                continue
    except Exception as e:
        time.sleep(5)
        with open('errors.txt', 'a') as f:
            f.write('\nMain: '+local_time+' '+str(e))
        continue
