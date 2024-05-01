import os
from datetime import datetime
from enum import StrEnum

from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from api import UserVkApi


class User:
    """Класс, описывающий пользователя социальной сети Вконтакте.

    Класс на вход принимает один параметр - item, находящийяся, в ответе на
    запрос 'users.search', в поле 'items'.
    :param data: является словарeм, описывающим поля пользователя
    """

    DT_FORMAT = '%d.%m.%Y'
    BASE_USER_URL = 'https://vk.com/id'

    def __init__(self, data: dict):
        self.id: int = data.get('id', 0)
        self.first_name: str = data.get('first_name', '')
        self.last_name: str = data.get('last_name', '')
        self.bdate: str = data.get('bdate', '')
        self.city_id: int = data.get('city', {}).get('id', 0)
        self.city_title: str = data.get('city', {}).get('id', '')
        self.sex: int = data.get('sex', 0)

    def get_age(self) -> int:
        if self.bdate:
            birthday = datetime.strptime(self.bdate, self.DT_FORMAT)
            cur_day = datetime.now()
            y, m, d = birthday.year, cur_day.month, cur_day.day
            return cur_day.year - y - (birthday > datetime(y, m, d))
        else:
            return 0

    def get_prf_link(self) -> str:
        return ''.join([self.BASE_USER_URL, str(self.id)])


class ActionInterface:

    def __init__(self):
        self.kb_is_act = False
        self.curr_action = {}
        self.curr_kb = None

    class KeyWord(StrEnum):
        ENOUGH = 'хватит'
        EXIT = 'exit'
        COME_BACK = 'назад'
        FND_PEOPLE = 'найти Далёких странников'
        FND_NEW_PEOPLE = 'найти новых людей'
        SHOW_FAVORITES = 'показать избранных'
        SHOW_BLACKLIST = 'показать неинтересных'
        CLEAR_BLACKLIST = 'очистить черный список'
        CLEAR_HISTORY = 'очистить историю просмотра'
        CHOOSE_AGE = 'выбрать возраст'
        CHOOSE_CITY = 'выбрать город'
        CHOOSE_SEX = 'выбрать пол'
        CHOOSE_INTERESTS = 'выбрать интересы'
        LETS_SHOW = 'показывай'
        IS_INTERESTING = 'интересно'
        IS_NOT_INTERESTING = 'не интересно'
        NEXT = 'следующий'
        PREVIOUS = 'предыдущий'

    def _get_start_dialog_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(self.KeyWord.FND_PEOPLE,
                            VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(self.KeyWord.ENOUGH, VkKeyboardColor.PRIMARY)

        key_word = {self.KeyWord.FND_PEOPLE: self._go_choose_view_options,
                    self.KeyWord.EXIT: self._exit_from_vkbot,
                    self.KeyWord.ENOUGH: self._stop_bot_dialog}
        return keyboard, key_word

    def _get_choosing_actions_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(self.KeyWord.FND_NEW_PEOPLE,
                            VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(self.KeyWord.SHOW_BLACKLIST,
                            VkKeyboardColor.POSITIVE)
        keyboard.add_button(self.KeyWord.SHOW_FAVORITES,
                            VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(self.KeyWord.CLEAR_BLACKLIST,
                            VkKeyboardColor.POSITIVE)
        keyboard.add_button(self.KeyWord.CLEAR_HISTORY,
                            VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(self.KeyWord.ENOUGH, VkKeyboardColor.POSITIVE)

        key_word = {self.KeyWord.FND_NEW_PEOPLE: self._go_search_people,
                    self.KeyWord.SHOW_BLACKLIST: self._go_blacklist_view,
                    self.KeyWord.SHOW_FAVORITES: self._go_favorites_view,
                    self.KeyWord.CLEAR_HISTORY: self._clear_history,
                    self.KeyWord.CLEAR_BLACKLIST: self._clear_blacklist,
                    self.KeyWord.EXIT: self._exit_from_vkbot,
                    self.KeyWord.ENOUGH: self._stop_bot_dialog}
        return keyboard, key_word

    def _get_criteria_selection_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(self.KeyWord.CHOOSE_CITY,
                            VkKeyboardColor.SECONDARY)
        keyboard.add_button(self.KeyWord.CHOOSE_AGE, VkKeyboardColor.SECONDARY)
        keyboard.add_button(self.KeyWord.CHOOSE_SEX, VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(self.KeyWord.CHOOSE_INTERESTS,
                            VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(self.KeyWord.LETS_SHOW, VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(self.KeyWord.COME_BACK, VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(self.KeyWord.ENOUGH, VkKeyboardColor.POSITIVE)

        key_word = {self.KeyWord.COME_BACK: self._come_back,
                    self.KeyWord.CHOOSE_CITY: self._choose_city,
                    self.KeyWord.CHOOSE_AGE: self._choose_age,
                    self.KeyWord.CHOOSE_SEX: self._choose_sex,
                    self.KeyWord.CHOOSE_INTERESTS: self._choose_interests,
                    self.KeyWord.LETS_SHOW: self._go_browsing,
                    self.KeyWord.EXIT: self._exit_from_vkbot,
                    self.KeyWord.ENOUGH: self._stop_bot_dialog}
        return keyboard, key_word

    def _get_queue_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(self.KeyWord.IS_NOT_INTERESTING,
                            VkKeyboardColor.SECONDARY)
        keyboard.add_button(self.KeyWord.IS_INTERESTING,
                            VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(self.KeyWord.NEXT, VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(self.KeyWord.COME_BACK, VkKeyboardColor.PRIMARY)
        keyboard.add_button(self.KeyWord.ENOUGH, VkKeyboardColor.PRIMARY)

        key_word = {self.KeyWord.IS_NOT_INTERESTING: self._add_to_blacklist,
                    self.KeyWord.IS_INTERESTING: self._add_to_favorites,
                    self.KeyWord.NEXT: self._show_next_user,
                    self.KeyWord.COME_BACK: self._come_back,
                    self.KeyWord.EXIT: self._exit_from_vkbot,
                    self.KeyWord.ENOUGH: self._stop_bot_dialog}
        return keyboard, key_word

    def _get_viewing_history_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(self.KeyWord.PREVIOUS, VkKeyboardColor.SECONDARY)
        keyboard.add_button(self.KeyWord.NEXT, VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(self.KeyWord.COME_BACK, VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(self.KeyWord.ENOUGH, VkKeyboardColor.POSITIVE)

        key_word = {self.KeyWord.NEXT: self._show_next_user,
                    self.KeyWord.PREVIOUS: self._show_previous_user,
                    self.KeyWord.COME_BACK: self._come_back,
                    self.KeyWord.EXIT: self._exit_from_vkbot,
                    self.KeyWord.ENOUGH: self._stop_bot_dialog}
        return keyboard, key_word

    # Реализация комыды "exit" и кнопки "хватит", общих для всего интерфейса
    def _exit_from_vkbot(self, message=''):
        pass

    def _stop_bot_dialog(self, message=''):
        pass

    # Реализация интерфейса стартовой клавиатуры
    def _start_bot_dialog(self, message=''):
        pass

    def _go_choose_view_options(self, message=''):
        pass

    # Реализация клавиатуры выбора вариантов просмотра пользователей
    def _go_search_people(self, message=''):
        pass

    def _go_blacklist_view(self, message=''):
        pass

    def _go_favorites_view(self, message=''):
        pass

    def _clear_history(self, message=''):
        pass

    def _clear_blacklist(self, message=''):
        pass

    # Реализация клавиатуры выбора опций поиска новых лидей
    def _choose_city(self, message=''):
        pass

    def _choose_age(self, message=''):
        pass

    def _choose_sex(self, message=''):
        pass

    def _choose_interests(self, message=''):
        pass

    def _choose_reserve_1(self, message=''):
        pass

    def _choose_reserve_2(self, message=''):
        pass

    def _go_browsing(self, message=''):
        pass

    # Реализация клавивтуры просмотра новых пользователей
    def _add_to_blacklist(self, message=''):
        pass

    def _add_to_favorites(self, message=''):
        pass

    # Реализация кнопки "предыдущий" клвавиатуры просмотра избранных
    def _show_previous_user(self, message=''):
        pass

    # Реализация кнопки "назад" и "следующий" общей для нескольких клавиатур
    def _come_back(self, message=''):
        pass

    def _show_next_user(self, message=''):
        pass


class Criteria:
    MIN_AGE = 1
    MAX_AGE = 120
    DEFAULT_SEX = [0, 1, 2]

    def __init__(self):
        self.age_from = self.MIN_AGE
        self.age_to = self.MAX_AGE
        self.sex = self.DEFAULT_SEX
        self.cities_id: list[int] = [0]
        self.fixed_criteria = False

    def check_user(self, user: User) -> bool:
        return all([self.check_sex(user.sex),
                    self.check_user_age(user.get_age()),
                    self.check_user_city(user.city_id)])

    def check_user_age(self, age: int) -> bool:
        return self.age_from <= age <= self.age_to

    def check_user_city(self, city_id: int) -> bool:
        return city_id in self.cities_id

    def check_sex(self, sex: int) -> bool:
        return sex in self.sex


class SearchEngine(Criteria):

    def __init__(self, user_token: str = None, user_id: int | str = None):
        super().__init__()
        self.user_api = UserVkApi(token=user_token, user_id=user_id)
        self.user_list = []
        self.offset = 0

        # self.have_access = data.get('can_access_closed', False)
        # self.is_closed = data.get('is_closed', True)

    def add_users_to_list(self):
        pass
