import os
import time

from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

# from db import ModelDb
from api import VkBotAPI, CurrVkApi, get_browser

# access_token = 'access_token'
# user_id = 'user_id'
# vk = VK(access_token, user_id)

# print(vk.users_info())
# токен полученный из инструкции


login_db = os.environ['LOGIN_DB']
password_db = os.environ['PASSWORD_DB']
token = os.environ['VK_TOKEN']
my_group_token = os.environ['MY_GROUP_TOKEN']
# vkapi = VkApi(token=my_group_token)
vkapi = CurrVkApi()
vkapi.get_token()

# vkbot = VkBotAPI(some_api=vkapi)

# key_word = {'привет': vkbot.show_keyboard,
#             'exit': vkbot.exit_from_vkbot,
#             'хватит': vkbot.hide_keyboard}
#
# # print(vkbot.vkapi.server_auth())
# for event in VkLongPoll(vkapi).listen():
#     if event.type == VkEventType.MESSAGE_NEW:
#         if event.to_me:
#             if not vkbot.is_active and event.text in key_word:
#                 key_word[event.text](event.user_id)
#             elif vkbot.is_active:
#                 if event.text in key_word:
#                     key_word[event.text](event.user_id)
#                 else:
#                     vkbot.write_msg(
#                         event.user_id,
#                         f'Что-то я тебя не пойму...'
#                     )
#                     # vkbot.get_person_info()
