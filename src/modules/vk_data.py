from datetime import datetime
from enum import StrEnum

from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class Meths(StrEnum):
    USERS_GET = 'users.get'
    MESSAGES_SEND = 'messages.send'
    USER_SEARCH = 'users.search'
    PHOTOS_GET = 'photos.get'
    GET_CITY = 'database.getCities'


class KeyWord(StrEnum):
    START_BOT = 'bot'
    STOP_BOT = 'хватит'
    EXIT_FROM_BOT = 'exit'
    COME_BACK = 'назад'
    FND_PEOPLE = 'найти Далёких странников'
    FND_NEW_PEOPLE = 'найти новых людей'
    SHOW_FAVORITES = 'показать избранных'
    SHOW_BLACKLIST = 'показать неинтересных'
    CLEAR_BLACKLIST = 'очистить черный список'
    CLEAR_HISTORY = 'очистить список избранных'
    CHOOSE_AGE = 'выбрать возраст'
    CHOOSE_CITY = 'выбрать город'
    CHOOSE_SEX = 'выбрать пол'
    CHOOSE_INTERESTS = 'выбрать интересы'
    LETS_SHOW = 'показывай'
    NEXT_USER = 'покажи ещё одного...'
    IS_INTERESTING = 'интересно'
    IS_NOT_INTERESTING = 'не интересно'
    PREVIOUS_PERSON = 'предыдущий'
    DELETE_FROM_LIST = 'удалить из списка'
    NEXT_PERSON = 'следующий'


class Photo:

    def __init__(self, data: dict):
        self.album_id = data.get('album_id', 0)
        self.date = data.get('date', 0)
        self.owner_id = data.get('owner_id', 0)
        self.photo_id = data.get('id', 0)
        self.photo_sizes = data.get('sizes', [])
        self.photo_link = data.get('sizes', [])[-1].get('url', '')
        self.count_likes = data.get('likes', {}).get('count', 0)
        self.user_likes = data.get('likes', {}).get('user_likes', 0)
        self.web_view_token = data.get('web_view_token', '')
        self.user_mark = False


class User:
    """Класс, описывающий пользователя социальной сети Вконтакте.

    Класс на вход принимает один параметр - item, находящийяся, в ответе на
    запрос 'users.search', в поле 'items'.
    :param data: является словарeм, описывающим поля пользователя
    """

    BASE_USER_URL = 'https://vk.com/id'

    def __init__(self, data: dict):
        self.id: int = data.get('id', 0)
        self.first_name: str = data.get('first_name', '')
        self.last_name: str = data.get('last_name', '')
        self.bdate: str = data.get('bdate', '')
        self.city_id: int = data.get('city', {}).get('id', 0)
        self.city_title: str = data.get('city', {}).get('title', '')
        self.sex: int = data.get('sex', 0)
        self.list_photos: list[Photo] = []

    def update_user_data(self, data: dict) -> None:
        """Обновляет информацию из"""
        self.id: int = data.get('id', 0)
        self.first_name: str = data.get('first_name', '')
        self.last_name: str = data.get('last_name', '')
        self.bdate: str = data.get('bdate', '')
        self.city_id: int = data.get('city', {}).get('id', 0)
        self.city_title: str = data.get('city', {}).get('id', '')
        self.sex: int = data.get('sex', 0)

    def get_age(self) -> int:
        if self.bdate:
            day, month, year = map(int, self.bdate.split('.'))
            birthday = datetime(year, month, day)
            cur_day = datetime.now()
            y, m, d = birthday.year, cur_day.month, cur_day.day
            return cur_day.year - y - (birthday > datetime(y, m, d))
        else:
            return 0

    def get_prf_link(self) -> str:
        return ''.join([self.BASE_USER_URL, str(self.id)])

    def get_user_info(self) -> str:
        text = (
            f'''
            {self.last_name} {self.first_name}
            {self.get_prf_link()}
            '''
        )
        return text

    def get_user_photos(self, count=3, popular=True) -> list[Photo]:
        self.list_photos.sort(key=lambda photo: photo.count_likes,
                              reverse=popular)
        return self.list_photos[:count]


class ActionInterface:

    def __init__(self):
        self.curr_action = {}
        self.curr_kb = None

    def _get_start_dialog_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(KeyWord.FND_PEOPLE, VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.STOP_BOT, VkKeyboardColor.PRIMARY)

        key_word = {KeyWord.FND_PEOPLE: self._go_choose_view_options,
                    KeyWord.STOP_BOT: self.stop_bot_dialog}
        return keyboard, key_word

    def _get_choosing_actions_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(KeyWord.FND_NEW_PEOPLE,
                            VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.SHOW_BLACKLIST,
                            VkKeyboardColor.POSITIVE)
        keyboard.add_button(KeyWord.SHOW_FAVORITES,
                            VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(KeyWord.CLEAR_BLACKLIST, VkKeyboardColor.POSITIVE)
        keyboard.add_button(KeyWord.CLEAR_HISTORY, VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(KeyWord.STOP_BOT, VkKeyboardColor.POSITIVE)

        key_word = {KeyWord.FND_NEW_PEOPLE: self._go_search_people,
                    KeyWord.SHOW_BLACKLIST: self._go_blacklist_view,
                    KeyWord.SHOW_FAVORITES: self._go_favorites_view,
                    KeyWord.CLEAR_HISTORY: self._clear_history,
                    KeyWord.CLEAR_BLACKLIST: self._clear_blacklist,
                    KeyWord.STOP_BOT: self.stop_bot_dialog}
        return keyboard, key_word

    def _get_criteria_selection_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(KeyWord.LETS_SHOW, VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.CHOOSE_CITY, VkKeyboardColor.SECONDARY)
        keyboard.add_button(KeyWord.CHOOSE_AGE, VkKeyboardColor.SECONDARY)
        keyboard.add_button(KeyWord.CHOOSE_SEX, VkKeyboardColor.POSITIVE)
        keyboard.add_button(KeyWord.CHOOSE_INTERESTS,
                            VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(KeyWord.COME_BACK, VkKeyboardColor.NEGATIVE)
        keyboard.add_button(KeyWord.STOP_BOT, VkKeyboardColor.POSITIVE)

        key_word = {KeyWord.COME_BACK: self._go_come_back,
                    KeyWord.CHOOSE_CITY: self._choose_city,
                    KeyWord.CHOOSE_AGE: self._choose_age,
                    KeyWord.CHOOSE_SEX: self._choose_sex,
                    KeyWord.CHOOSE_INTERESTS: self._choose_interests,
                    KeyWord.LETS_SHOW: self._go_browsing,
                    KeyWord.STOP_BOT: self.stop_bot_dialog}
        return keyboard, key_word

    def _get_queue_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(KeyWord.IS_NOT_INTERESTING,
                            VkKeyboardColor.SECONDARY)
        keyboard.add_button(KeyWord.IS_INTERESTING,
                            VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.NEXT_USER, VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.COME_BACK, VkKeyboardColor.PRIMARY)
        keyboard.add_button(KeyWord.STOP_BOT, VkKeyboardColor.PRIMARY)

        key_word = {KeyWord.IS_NOT_INTERESTING: self._add_to_blacklist,
                    KeyWord.IS_INTERESTING: self._add_to_favorites,
                    KeyWord.NEXT_USER: self._show_next_user,
                    KeyWord.COME_BACK: self._go_come_back,
                    KeyWord.STOP_BOT: self.stop_bot_dialog}
        return keyboard, key_word

    def _get_viewing_history_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button(KeyWord.PREVIOUS_PERSON, VkKeyboardColor.SECONDARY)
        keyboard.add_button(KeyWord.DELETE_FROM_LIST, VkKeyboardColor.NEGATIVE)
        keyboard.add_button(KeyWord.NEXT_PERSON, VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(KeyWord.COME_BACK, VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(KeyWord.STOP_BOT, VkKeyboardColor.POSITIVE)

        key_word = {KeyWord.NEXT_PERSON: self._show_next_person(),
                    KeyWord.DELETE_FROM_LIST: self._delete_user,
                    KeyWord.PREVIOUS_PERSON: self._show_previous_person(),
                    KeyWord.COME_BACK: self._go_come_back,
                    KeyWord.STOP_BOT: self.stop_bot_dialog}
        return keyboard, key_word

    # Реализация комыды "exit" и кнопки "хватит", общих для всего интерфейса
    def exit_from_vkbot(self, message=''):
        pass

    def stop_bot_dialog(self, message=''):
        pass

    # Реализация интерфейса стартовой клавиатуры
    def start_bot_dialog(self, message=''):
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

    def _show_next_user(self):
        pass

    # Реализация клавивтуры просмотра новых пользователей
    def _add_to_blacklist(self, message=''):
        pass

    def _add_to_favorites(self, message=''):
        pass

    # Реализация кнопки "предыдущий" клвавиатуры просмотра избранных
    def _show_previous_user(self, message=''):
        pass

    def _show_previous_person(self, message=''):
        pass

    def _delete_user(self, message=''):
        pass

    def _show_next_person(self, message=''):
        pass

    # Реализация кнопки "назад" и "следующий" общей для нескольких клавиатур
    def _go_come_back(self, message=''):
        pass
