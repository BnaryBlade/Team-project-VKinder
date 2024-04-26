import os

from vk_api import VkApi
from api import VKBot
from vk_api.longpoll import VkLongPoll, VkEventType

token = os.environ['VK_TOKEN']
vkapi = VkApi(token=token)
vkbot = VKBot(api=vkapi)

key_word = {'привет': vkbot.show_keyboard,
            'exit': vkbot.exit_from_vkbot,
            'хватит': vkbot.hide_keyboard}

for event in VkLongPoll(vkapi).listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            if not vkbot.is_active and event.text in key_word:
                key_word[event.text](event.user_id)
            elif vkbot.is_active:
                if event.text in key_word:
                    key_word[event.text](event.user_id)
                else:
                    vkbot.write_msg(
                        event.user_id,
                        f'Что-то я тебя не пойму...'
                    )
