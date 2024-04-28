import os

from vk_api.longpoll import VkLongPoll, VkEventType

# from db import ModelDb
from api import UserVkApi, BotVkApi

# access_token = 'access_token'
# user_id = 'user_id'
# vk = VK(access_token, user_id)

# print(vk.users_info())
# токен полученный из инструкции


login_db = os.environ['LOGIN_DB']
password_db = os.environ['PASSWORD_DB']
group_token = os.environ['GROUP_TOKEN']
my_group_token = os.environ['MY_GROUP_TOKEN']

app_id = int(os.environ['APP_ID'])
my_token = os.environ['TOKEN']
my_id = int(os.environ['USER_ID'])

user_api = UserVkApi(token=my_token, user_id=my_id)
bot_api = BotVkApi(group_token=group_token)

key_word = {'привет': bot_api.show_keyboard,
            'exit': bot_api.exit_from_vkbot,
            'хватит': bot_api.hide_keyboard}


for event in VkLongPoll(bot_api).listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            if not bot_api.bot_is_active and event.text in key_word:
                key_word[event.text](event.user_id)
            elif bot_api.bot_is_active:
                if event.text in key_word:
                    key_word[event.text](event.user_id)
                else:
                    bot_api.write_msg(
                        event.user_id,
                        f'Что-то я тебя не пойму...'
                    )
                    # vkbot.get_person_info()
