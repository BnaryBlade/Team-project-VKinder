import os
import re
from typing import Any

from vk_api.longpoll import VkLongPoll, VkEventType, Event

from db import ModelDb
from vk_data import ActionInterface, User
from api import BotVkApi
from classes import SearchEngine


class Bot(ModelDb, ActionInterface):
    AGE_PATTERN = re.compile(r'\d{1,3}')
    SEX_PATTERN = re.compile(r'')

    def __init__(self, group_token: str,
                 login_db: str,
                 password_db: str,
                 user_token: str = None,
                 user_id: int | str = None,
                 db_name='vk_bot_db', ) -> None:
        super().__init__(login=login_db, password=password_db, db_name=db_name)
        self.s_engin = SearchEngine(user_token, user_id)
        self.api = BotVkApi(group_token=group_token)
        self.bot_is_act = False
        self.bot_is_sleep = True
        self.client: User | None = None
        # self.curr_id: int | None = None
        self.another_action: Any = None
        # self.found_user: User | None = None

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
                if self.client is None:
                    user_data = self.s_engin.api.get_users_info(
                        [event.user_id]
                    )
                    self.client = User(user_data[0])
                if not self.bot_is_sleep:
                    self.select_action(event)
                elif event.text == 'bot':
                    self.bot_is_sleep = False
                    self._start_bot_dialog()
        # self.curr_id = None

    def select_action(self, event: Event) -> None:
        if (action := self.curr_action.get(event.text)) is not None:
            action()
        else:
            self.another_action(event)

    def _exit_from_vkbot(self, message='') -> None:
        message = 'Убил...'
        if self.api.hide_kb(self.client.id, message,
                            self.curr_kb.get_empty_keyboard()):
            self.kb_is_act = False
        self.bot_is_act = False

    def _start_bot_dialog(self, message='') -> None:
        self.curr_kb, self.curr_action = self._get_start_dialog_kb()
        self.another_action = self.do_another_action
        message = 'А вот и я... :-)'
        if bot.api.show_kb(self.client.id, message,
                           self.curr_kb.get_keyboard()):
            self.kb_is_act = True
            self.s_engin.set_criteria_from_user(self.client)

    def _stop_bot_dialog(self, message='') -> None:
        if self.s_engin.is_criteria_changed:
            self.s_engin.stop_found_users()
            self.s_engin.set_criteria_from_user(self.client)
        if self.bot_is_act:
            message = 'Ладно, и мне пора... :-)'
            if self.api.hide_kb(self.client.id, message,
                                self.curr_kb.get_empty_keyboard()):
                self.kb_is_act = False
        self.bot_is_sleep = True

    def _go_choose_view_options(self,
                                message='Где будем просматривать?') -> None:
        self.curr_kb, self.curr_action = self._get_choosing_actions_kb()
        self.api.show_kb(self.client.id, message, self.curr_kb.get_keyboard())

    def _go_blacklist_view(self, message='Посмотрим...') -> None:
        self.curr_kb, self.curr_action = self._get_viewing_history_kb()
        self.api.show_kb(self.client.id, message, self.curr_kb.get_keyboard())

    def _go_favorites_view(self, message='Посмотрим...') -> None:
        self.curr_kb, self.curr_action = self._get_viewing_history_kb()
        self.api.show_kb(self.client.id, message, self.curr_kb.get_keyboard())

    def _go_search_people(self, message='') -> None:
        self.curr_kb, self.curr_action = self._get_criteria_selection_kb()
        message = self.s_engin.get_descr_criteria()
        self.api.show_kb(self.client.id, message, self.curr_kb.get_keyboard())
        self.api.write_msg(self.client.id,
                           'Но можете изменить эти данные...')

    def _clear_history(self, message='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, message)

    def _clear_blacklist(self, message='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, message)

    def _go_come_back(self, message='Передумали... :-(') -> None:
        if self.s_engin.is_criteria_changed:
            self.s_engin.stop_found_users()
            self.s_engin.set_criteria_from_user(self.client)
        self.curr_kb, self.curr_action = self._get_choosing_actions_kb()
        self.api.show_kb(self.client.id, message, self.curr_kb.get_keyboard())

    def _choose_city(self, message='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, message)

    def _checking_city(self, event: Event):
        pass

    def _choose_age(self,
                    message=('укажите от какого и до какого возраста вас'
                             ' интересуют люди...')) -> None:
        if self.api.hide_kb(self.client.id, message,
                            self.curr_kb.get_empty_keyboard()):
            self.curr_action = {self.KeyWord.ENOUGH: self._stop_bot_dialog,
                                self.KeyWord.EXIT: self._exit_from_vkbot,
                                self.KeyWord.COME_BACK: self._go_come_back}
            self.another_action = self._checking_age_input

    def _checking_age_input(self, event: Event) -> None:
        if all_ages := self.AGE_PATTERN.findall(event.text):
            try:
                all_ages = list(
                    filter(lambda age: 0 < age < 120, map(int, all_ages))
                )
                self.s_engin.age_from = min(all_ages)
                self.s_engin.age_to = max(all_ages)
                self.s_engin.is_criteria_changed = True
            except ValueError:
                self.api.write_msg(
                    self.client.id,
                    'Что-то я не понял какой возраст мне искать...')
            else:
                message = self.s_engin.get_descr_criteria()
                self._go_search_people(message)
        else:
            self.api.write_msg(self.client.id,
                               'Вы не указали ни одного возраста...')
            self.api.write_msg(
                self.client.id,
                ('Если передумали - наберите "нзад", чтобы вернуться'
                 ' или "хватит, чтобы прервать диалог..."'))

    def _choose_sex(self, message='Укажите, кто вас интересует:') -> None:
        if self.api.hide_kb(self.client.id, message,
                            self.curr_kb.get_empty_keyboard()):
            self.curr_action = {self.KeyWord.ENOUGH: self._stop_bot_dialog,
                                self.KeyWord.EXIT: self._exit_from_vkbot,
                                self.KeyWord.COME_BACK: self._go_come_back}
            self.another_action = self._checking_sex_input
            self.api.write_msg(self.client.id, '- не имеет значения: "0";')
            self.api.write_msg(self.client.id, '- люди женского пола: "1";')
            self.api.write_msg(self.client.id, '- люди мужского пола: "2".')

    def _checking_sex_input(self, event: Event) -> None:
        self.api.write_msg(self.client.id,
                           ' - '.join([event.text, 'мой ответ']))
        self.s_engin.is_criteria_changed = True

    def _choose_interests(self, message='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, message)

    def _choose_reserve_1(self, message='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, message)

    def _choose_reserve_2(self, message='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, message)

    def _go_browsing(self, message='Поищем...') -> None:
        self.curr_kb, self.curr_action = self._get_queue_kb()
        self.api.show_kb(self.client.id, message, self.curr_kb.get_keyboard())
        user = self.s_engin.start_found_users()
        self.show_user_info(user)
        self.show_user_photos(user)

    def _add_to_blacklist(self, message='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, message)

    def _add_to_favorites(self, message='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, message)

    def _show_previous_user(self,
                            message='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, message)

    def _show_next_user(self) -> None:
        user = self.s_engin.get_next_user()
        self.show_user_info(user)
        self.show_user_photos(user)

    def do_another_action(self, event: Event) -> None:
        text = event.text
        self.api.write_msg(
            self.client.id,
            ' - '.join([text,
                        'Я не совсем понимаю, чего вы от меня хотите...'])
        )

    def show_user_info(self, user: User) -> None:
        message = user.get_user_info()
        self.api.write_msg(self.client.id, message)

    def show_user_photos(self, user: User) -> None:
        attachments = []
        for pht in user.get_user_photos():
            attachment = f'photo{pht.owner_id}_{pht.photo_id}'
            attachments.append(attachment)
        self.api.send_attachment(self.client.id, ','.join(attachments))


if __name__ == '__main__':
    lgn_db = os.environ['LOGIN_DB']
    pass_db = os.environ['PASSWORD_DB']
    grp_token = os.environ['GROUP_TOKEN']
    my_group_token = os.environ['MY_GROUP_TOKEN']

    app_id = int(os.environ['APP_ID'])
    my_token = os.environ['TOKEN']
    my_id = int(os.environ['USER_ID'])

    bot = Bot(my_group_token, lgn_db, pass_db, my_token, my_id)
    bot.start()
    # print(bot.s_engin.api.search_users_1(5))
    # bot.s_engin.get_data_users()
    # print(bot.s_engin.api.get_users_info())
