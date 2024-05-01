from datetime import datetime
from enum import StrEnum

from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from api import UserVkApi


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
        self.list_photos: list[Photo] = []

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

    def _show_next_user(self):
        pass


class Criteria:
    MIN_AGE = 1
    MAX_AGE = 120
    DEFAULT_SEX = [0, 1, 2]
    STR_SEX = {0: 'неуказан', 1: 'женский', 2: 'мужской'}

    def __init__(self):
        self.age_from = self.MIN_AGE
        self.age_to = self.MAX_AGE
        self.sex = self.DEFAULT_SEX
        self.cities_id: list[int] = [0, 21, 1]
        self.city_title = ''
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
    STEP_SEARCH = 10

    def __init__(self, user_token: str = None, user_id: int | str = None):
        super().__init__()
        self.api = UserVkApi(token=user_token, user_id=user_id)
        self.user_list = []
        self.offset = 0

    def get_data_users(self) -> bool:
        if users_data := self.api.search_users(
                self.STEP_SEARCH, self.api.search_params, self.api.fields,
                self.offset):
            self.offset += self.STEP_SEARCH
            for data in users_data:
                if not data.get('is_closed', 1):
                    user = User(data)
                    if self.check_user(user):
                        user.list_photos = self.upload_photos(user.id)
                        self.user_list.append(user)
            return True
        else:
            return False

    def upload_photos(self, user_id: int) -> list[Photo]:
        if user_photos := self.api.get_user_photos(user_id):
            photos = []
            for data in user_photos:
                photo = Photo(data)
                photos.append(photo)
            return photos
        else:
            return []

    def get_next_user(self) -> User | None:
        if self.user_list:
            return self.user_list.pop(0)
        else:
            self.get_data_users()
            try:
                return self.user_list.pop(0)
            except IndexError:
                print('Больше пользователей согласно заданных критериев '
                      'найти не получается!!!')
                return None

    def get_descr_criteria(self) -> str:
        str_sex = self.STR_SEX.get(min(self.sex), 'неважен')
        text = (
            f'''
            - возраст: от {self.age_from} до {self.age_to} лет;
            - пол: {str_sex};
            - город: {self.city_title}.
            '''
        )
        return text
