import os

from vk_api.longpoll import VkLongPoll, VkEventType, Event

from db import ModelDb
from api import UserVkApi, BotVkApi
from vk_data import ActionInterface

lgn_db = os.environ['LOGIN_DB']
pass_db = os.environ['PASSWORD_DB']
grp_token = os.environ['GROUP_TOKEN']
my_grp_token = os.environ['MY_GROUP_TOKEN']

app_id = int(os.environ['APP_ID'])
my_token = os.environ['TOKEN']
my_id = int(os.environ['USER_ID'])


class Bot(ModelDb, ActionInterface):

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
        self.bot_is_sleep = True
        self.curr_id: int | None = None

    def start(self) -> None:
        self.bot_is_act = True
        for event in VkLongPoll(self.api).listen():
            if self.bot_is_act:
                self.event_handling(event)
            else:
                break

    def event_handling(self, event: Event) -> None:
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                self.curr_id = event.user_id
                if not self.bot_is_sleep:
                    self.select_action(event)
                elif event.text == 'bot':
                    self.bot_is_sleep = False
                    self.start_bot_dialog()
        self.curr_id = None

    def select_action(self, event: Event) -> None:
        if (action := self.curr_action.get(event.text)) is not None:
            action()
        else:
            self.api.write_msg(
                self.curr_id,
                'Я не совсем понимаю, чего вы от меня хотите...'
            )

    def show_keyboard(self, message: str):
        if bot.api.show_keyboard(self.curr_id, message, self.curr_kb):
            self.kb_is_act = True

    def exit_from_vkbot(self):
        if self.api.hide_keyboard(self.curr_id, 'Убил...'):
            self.kb_is_act = False
        else:
            print('Не получилось отключить клавиатуру...')
        self.bot_is_act = False

    def hide_keyboard(self):
        if self.bot_is_act:
            if self.api.hide_keyboard(self.curr_id):
                self.kb_is_act = False
            else:
                print('Не получилось убрать клавиатуру')

    def start_bot_dialog(self):
        super().start_bot_dialog()
        message = 'А вот и я... :-)'
        self.show_keyboard(message)

    def stop_bot_dialog(self):
        self.hide_keyboard()
        self.bot_is_sleep = True

    def search_people(self):
        super().search_people()
        message = 'Давай выберем критерии поиска... :-)'
        self.show_keyboard(message)

    def come_back(self):
        super().come_back()
        message = 'Передумали... :-('
        self.show_keyboard(message)

    def choose_city(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def choose_age(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def choose_sex(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def choose_reserve_1(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def choose_reserve_2(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def start_browsing(self):
        super().start_browsing()
        message = 'Пока ещё не реализовали...'
        self.show_keyboard(message)

    def add_to_blacklist(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def add_to_favorites(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def show_next_user(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)


if __name__ == '__main__':
    bot = Bot(grp_token, lgn_db, pass_db, my_token, my_id)
    print(bot.user_api.search_users(5))
    # bot.start()
