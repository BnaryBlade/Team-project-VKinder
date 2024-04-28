import os
from typing import Any

from vk_api.longpoll import VkLongPoll, VkEventType, Event

from db import ModelDb
from api import UserVkApi, BotVkApi

lgn_db = os.environ['LOGIN_DB']
pass_db = os.environ['PASSWORD_DB']
grp_token = os.environ['GROUP_TOKEN']
my_grp_token = os.environ['MY_GROUP_TOKEN']

app_id = int(os.environ['APP_ID'])
my_token = os.environ['TOKEN']
my_id = int(os.environ['USER_ID'])


class Bot(ModelDb):

    def __init__(self, group_token: str,
                 login_db: str,
                 password_db: str,
                 user_token: str = None,
                 user_id: int | str = None,
                 db_name='vk_bot_db', ) -> None:
        super().__init__(login=login_db, password=password_db, db_name=db_name)
        self.user_api = UserVkApi(token=user_token, user_id=user_id)
        self.api = BotVkApi(group_token=group_token)
        self.bot_is_act = False
        self.kb_is_act = False
        self.curr_action = {'привет': self.show_keyboard,
                            'exit': self.exit_from_vkbot,
                            'хватит': self.hide_keyboard}

    def event_handling(self, event: Event) -> None:
        # key_word = {'привет': self.show_keyboard,
        #             'exit': self.exit_from_vkbot,
        #             'хватит': self.hide_keyboard}
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                if action := self.select_action_on_message(event.text):
                    action(event.user_id)
                else:
                    bot.api.write_msg(event.user_id,
                                      f'Что-то я тебя не пойму...')

    def show_keyboard(self, user_id: int):
        if not self.kb_is_act and bot.api.show_keyboard(user_id):
            self.kb_is_act = True

    def exit_from_vkbot(self, user_id: int):
        if self.api.hide_keyboard(user_id, 'Убил...'):
            self.kb_is_act = False
        else:
            print('Не получилось отключить клавиатуру...')
        self.bot_is_act = False

    def start(self) -> None:
        self.bot_is_act = True
        for event in VkLongPoll(self.api).listen():
            if self.bot_is_act:
                self.event_handling(event)
            else:
                break

    def select_action_on_message(self, text: str) -> Any:
        variants = {
            'привет': self.show_keyboard,
            'exit': self.exit_from_vkbot,
            'хватит': self.hide_keyboard,
            'Хочу найти интересного человека': None
        }
        action = variants.get(text)
        return action if action is not None else False

    def hide_keyboard(self, user_id: int):
        if self.bot_is_act:
            if self.api.hide_keyboard(user_id):
                self.kb_is_act = False
            else:
                print('Не получилось убрать клавиатуру')


if __name__ == '__main__':
    bot = Bot(grp_token, lgn_db, pass_db, my_token, my_id)
    bot.start()
    #
    # for event in VkLongPoll(bot.api).listen():
    #     if event.type == VkEventType.MESSAGE_NEW:
    #         if event.to_me:
    #             if not bot.api.b_is_active and event.text in key_word:
    #                 key_word[event.text](event.user_id)
    #             elif bot.api.b_is_active:
    #                 if event.text in key_word:
    #                     key_word[event.text](event.user_id)
    #                 else:
    #                     bot.api.write_msg(
    #                         event.user_id,
    #                         f'Что-то я тебя не пойму...'
    #                     )
    #                     # vkbot.get_person_info()
