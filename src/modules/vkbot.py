import os
import re
from typing import Any

from vk_api.longpoll import VkLongPoll, VkEventType, Event

from db import ModelDb
from vk_data import ActionInterface, User, KeyWord
from api import BotVkApi, UserVkApi
from classes import SearchEngine


class Bot(ActionInterface):
    AGE_PATTERN = re.compile(r'\d{1,3}')

    def __init__(self, user_api: UserVkApi, user: User,
                 bot_api: BotVkApi, model_db: ModelDb) -> None:
        super().__init__()
        self.s_engin = SearchEngine(user_api)
        self.api = bot_api
        self.db = model_db
        self.client = user
        self.another_action: Any = None

    def event_handling(self, event: Event) -> None:
        action = self.curr_action.get(event.text)
        if action is not None:
            action()
        else:
            self.another_action(event)

    def start_bot_dialog(self, msg='') -> None:
        self.curr_kb, self.curr_action = self._get_start_dialog_kb()
        self.another_action = self.do_another_action
        self.s_engin.set_criteria_from_user(self.client)
        self.api.show_kb(self.client.id, msg, self.curr_kb.get_keyboard())

    def stop_bot_dialog(self, msg='Ладно, и мне пора... :-)') -> None:
        self.api.hide_kb(self.client.id, msg,
                         self.curr_kb.get_empty_keyboard())

    def _go_choose_view_options(self, msg='Где будем просматривать?') -> None:
        self.curr_kb, self.curr_action = self._get_choosing_actions_kb()
        self.api.show_kb(self.client.id, msg, self.curr_kb.get_keyboard())

    def _go_blacklist_view(self, msg='Посмотрим...') -> None:
        self.curr_kb, self.curr_action = self._get_viewing_history_kb()
        self.api.show_kb(self.client.id, msg, self.curr_kb.get_keyboard())

    def _go_favorites_view(self, msg='Посмотрим...') -> None:
        self.curr_kb, self.curr_action = self._get_viewing_history_kb()
        self.api.show_kb(self.client.id, msg, self.curr_kb.get_keyboard())

    def _go_search_people(self, msg='') -> None:
        self.curr_kb, self.curr_action = self._get_criteria_selection_kb()
        msg = self.s_engin.get_descr_criteria()
        self.api.show_kb(self.client.id, msg, self.curr_kb.get_keyboard())
        self.another_action = self.do_another_action
        self.api.write_msg(self.client.id, 'Но можете изменить эти данные...')

    def _clear_history(self, msg='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def _clear_blacklist(self, msg='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def _go_come_back(self, msg='Передумали... :-(') -> None:
        if self.s_engin.is_search_going_on:
            self.s_engin.stop_found_users()
            self.s_engin.set_criteria_from_user(self.client)
        elif self.s_engin.is_criteria_changed:
            self.s_engin.set_criteria_from_user(self.client)
        self.curr_kb, self.curr_action = self._get_choosing_actions_kb()
        self.api.show_kb(self.client.id, msg, self.curr_kb.get_keyboard())

    def _choose_city(self, msg='') -> None:
        msg = 'Напишите название города, в котором будем искать людей...'
        if self.api.hide_kb(self.client.id, msg,
                            self.curr_kb.get_empty_keyboard()):
            self.curr_action = {KeyWord.STOP_BOT: self.stop_bot_dialog,
                                KeyWord.COME_BACK: self._go_come_back}
            self.another_action = self._checking_city

    def _choose_age(self, msg='') -> None:
        msg = 'Укажите от какого и до какого возраста Вас интересуют люди...'
        self.api.hide_kb(self.client.id, msg,
                         self.curr_kb.get_empty_keyboard())
        self.curr_action = {KeyWord.STOP_BOT: self.stop_bot_dialog,
                            KeyWord.COME_BACK: self._go_come_back}
        self.another_action = self._checking_age_input

    def _choose_sex(self, msg='') -> None:
        msg = ('Укажите, кто вас интересует:\n'
               '\t"0" - не имеет значения;\n'
               '\t"1" - люди женского пола;\n'
               '\t"2" - люди мужского пола.')
        self.api.hide_kb(self.client.id, msg,
                         self.curr_kb.get_empty_keyboard())
        self.curr_action = {KeyWord.STOP_BOT: self.stop_bot_dialog,
                            KeyWord.COME_BACK: self._go_come_back}
        self.another_action = self._checking_sex_input

    def _checking_city(self, event: Event):
        if city := self.s_engin.search_city(event.text, 1):
            self.s_engin.city_id = city[0].get('id', self.client.city_id)
            self.s_engin.city_title = city[0].get('title',
                                                  self.client.city_title)
            self.s_engin.is_criteria_changed = True
            msg = self.s_engin.get_descr_criteria()
            self._go_search_people(msg)
        else:
            self.api.write_msg(self.client.id,
                               'Такой город я не знаю: введите'
                               ' другое название!\nИли, если передумали - '
                               'то наберите "назад", чтобы вернуться или '
                               '"хватит", чтобы закончить нашу беседу...')

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
                msg = self.s_engin.get_descr_criteria()
                self._go_search_people(msg)
        else:
            self.api.write_msg(self.client.id,
                               'Вы не указали ни одного возраста...')
            self.api.write_msg(
                self.client.id,
                'Если передумали - наберите "назад", чтобы вернуться'
                ' или "хватит", чтобы прервать диалог...')

    def _checking_sex_input(self, event: Event) -> None:
        try:
            sex = int(event.text)
        except ValueError:
            self.api.write_msg(self.client.id,
                               'Введите пожалуйста только одну цифру: "0" или'
                               ' "1" или "2"!\nЕсли передумали - наберите '
                               '"назад", чтобы вернуться или "хватит", чтобы'
                               ' прервать диалог...')
        else:
            if sex not in [0, 1, 2]:
                self.api.write_msg(self.client.id,
                                   'цифра введена неправильная...'
                                   ' попробуйте ещё раз...\nЕсли передумали - '
                                   'наберите "назад", чтобы вернуться или'
                                   ' "хватит", чтобы прервать диалог...')
            else:
                self.s_engin.sex = sex
                self.s_engin.is_criteria_changed = True
                msg = self.s_engin.get_descr_criteria()
                self._go_search_people(msg)

    def _choose_interests(self, msg='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def _choose_reserve_1(self, msg='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def _choose_reserve_2(self, msg='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def _go_browsing(self, msg='Поищем...') -> None:
        self.curr_kb, self.curr_action = self._get_queue_kb()
        self.api.show_kb(self.client.id, msg, self.curr_kb.get_keyboard())
        user = self.s_engin.start_found_users()
        if user is not None:
            self.show_user_info(user)
        else:
            self.api.write_msg(self.client.id, 'Нет таких пользователей')
            self._go_come_back('Может изменить критерии')

    def _show_next_user(self) -> None:
        user = self.s_engin.get_next_user()
        if user is not None:
            self.show_user_info(user)
        else:
            self.api.write_msg(self.client.id, 'Нет таких пользователей')
            self._go_come_back('Может изменить критерии')

    def _add_to_blacklist(self, msg='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def _add_to_favorites(self, msg='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def _show_previous_user(self, msg='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def _show_previous_person(self, msg='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def _delete_user(self, msg='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def _show_next_person(self, msg='Пока ещё не реализовали...') -> None:
        self.api.write_msg(self.client.id, msg)

    def do_another_action(self, event: Event) -> None:
        msg = '-'.join([event.text, 'я не понимаю, чего Вы от меня хотите...'])
        self.api.write_msg(self.client.id, msg)

    def show_user_info(self, user: User) -> None:
        msg = user.get_user_info()
        attachments = []
        for pht in user.get_user_photos():
            attachment = f'photo{pht.owner_id}_{pht.photo_id}'
            attachments.append(attachment)
        self.api.send_attachment(self.client.id, msg, ','.join(attachments))


if __name__ == '__main__':
    lgn_db = os.environ['LOGIN_DB']
    pass_db = os.environ['PASSWORD_DB']
    # grp_token = os.environ['GROUP_TOKEN']
    my_group_token = os.environ['MY_GROUP_TOKEN']

    app_id = int(os.environ['APP_ID'])
    my_token = os.environ['TOKEN']
    my_id = int(os.environ['USER_ID'])

    admin_api = UserVkApi(token=my_token, user_id=my_id)
    group_api = BotVkApi(group_token=my_group_token)
    database = ModelDb(login=lgn_db, password=pass_db, db_name='vk_bot_db')

    all_bots: dict[Bot] | dict = {}

    for next_event in VkLongPoll(group_api).listen():
        if next_event.type == VkEventType.MESSAGE_NEW:
            if next_event.to_me:
                if (next_event.user_id == admin_api.admin.id
                        and next_event.text == KeyWord.EXIT_FROM_BOT):
                    break
                if next_event.user_id in all_bots:
                    curr_bot = all_bots.get(next_event.user_id)
                    if isinstance(curr_bot, Bot):
                        if next_event.text == KeyWord.STOP_BOT:
                            curr_bot.stop_bot_dialog()
                            all_bots.pop(next_event.user_id)
                        else:
                            curr_bot.event_handling(next_event)
                else:
                    if next_event.text.lower() == KeyWord.START_BOT:
                        next_client = User(
                            admin_api.get_users_info([next_event.user_id])[0]
                        )
                        next_bot = Bot(user_api=admin_api, bot_api=group_api,
                                       model_db=database, user=next_client)
                        message = 'Я снова с Вами... :-)'
                        next_bot.start_bot_dialog(message)
                        all_bots[next_event.user_id] = next_bot

    message = 'Админ меня убил... :-('
    for _, next_bot in all_bots.items():
        next_bot.stop_bot_dialog(message)
    all_bots.clear()

    # bot = Bot(my_group_token, lgn_db, pass_db, my_token, my_id)
    # bot.start()
    # print(bot.s_engin.api.search_users_1(5))
    # bot.s_engin.get_data_users()
    # print(bot.s_engin.api.get_users_info())
