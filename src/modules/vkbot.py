import os

from vk_api.longpoll import VkLongPoll, VkEventType, Event

from db import ModelDb
from api import UserVkApi, BotVkApi
from vk_data import ActionInterface

lgn_db = os.environ['LOGIN_DB']
pass_db = os.environ['PASSWORD_DB']
grp_token = os.environ['GROUP_TOKEN']
my_group_token = os.environ['MY_GROUP_TOKEN']

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
                    self._start_bot_dialog()
        self.curr_id = None

    def select_action(self, event: Event) -> None:
        if (action := self.curr_action.get(event.text)) is not None:
            action()
        else:
            self.api.write_msg(
                self.curr_id,
                'Я не совсем понимаю, чего вы от меня хотите...'
            )

    def _exit_from_vkbot(self) -> None:
        message = 'Убил...'
        if self.api.hide_kb(self.curr_id, message,
                            self.curr_kb.get_empty_keyboard()):
            self.kb_is_act = False
        self.bot_is_act = False

    def _start_bot_dialog(self) -> None:
        self.curr_kb, self.curr_action = self._get_start_dialog_kb()
        message = 'А вот и я... :-)'
        if bot.api.show_kb(self.curr_id, message,
                           self.curr_kb.get_keyboard()):
            self.kb_is_act = True

    def _stop_bot_dialog(self):
        if self.bot_is_act:
            message = 'Ладно, и мне пора... :-)'
            if self.api.hide_kb(self.curr_id, message,
                                self.curr_kb.get_empty_keyboard()):
                self.kb_is_act = False
        self.bot_is_sleep = True

    def _go_choose_view_options(self):
        self.curr_kb, self.curr_action = self._get_choosing_actions_kb()
        message = 'Где будем просматривать?'
        self.api.show_kb(self.curr_id, message, self.curr_kb.get_keyboard())

    def _go_blacklist_view(self):
        self.curr_kb, self.curr_action = self._get_viewing_history_kb()
        message = 'Посмотрим...'
        self.api.show_kb(self.curr_id, message, self.curr_kb.get_keyboard())

    def _go_favorites_view(self):
        self.curr_kb, self.curr_action = self._get_viewing_history_kb()
        message = 'Посмотрим...'
        self.api.show_kb(self.curr_id, message, self.curr_kb.get_keyboard())

    def _go_search_people(self):
        self.curr_kb, self.curr_action = self._get_criteria_selection_kb()
        message = 'Можете выбрать критерии поиска...'
        if bot.api.show_kb(self.curr_id, message, self.curr_kb.get_keyboard()):
            self.kb_is_act = True
            self.api.write_msg(
                self.curr_id,
                'По умолчанию буду ориентироваться на ваши данные...:-)'
            )

    def _clear_history(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def _clear_blacklist(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def _come_back(self):
        self.curr_kb, self.curr_action = self._get_choosing_actions_kb()
        message = 'Передумали... :-('
        self.api.show_kb(self.curr_id, message, self.curr_kb.get_keyboard())

    def _choose_city(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def _choose_age(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def _choose_sex(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def _choose_reserve_1(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def _choose_reserve_2(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def _go_browsing(self):
        self.curr_kb, self.curr_action = self._get_queue_kb()
        message = 'Поищем...'
        self.api.show_kb(self.curr_id, message, self.curr_kb.get_keyboard())

    def _add_to_blacklist(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def _add_to_favorites(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def _show_previous_user(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)

    def _show_next_user(self):
        message = 'Пока ещё не реализовали...'
        self.api.write_msg(self.curr_id, message)


if __name__ == '__main__':
    bot = Bot(grp_token, lgn_db, pass_db, my_token, my_id)
    bot.start()
    # print(bot.user_api.search_users(1))
