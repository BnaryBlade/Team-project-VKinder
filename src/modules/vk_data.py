import os
from datetime import datetime
from enum import StrEnum

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


def get_paths() -> tuple[str, str]:
    """Функция возвращает пути расположения firefox и geckodriver"""
    install_dir = '/snap/firefox/current/usr/lib/firefox'
    driver_loc = os.path.join(install_dir, "geckodriver")
    binary_loc = os.path.join(install_dir, "firefox")
    return binary_loc, driver_loc


def get_browser(binary_loc: str | None = None,
                driver_loc: str | None = None) -> webdriver.Firefox:
    """Возращает объект webdriver Firefox.

    Функция создаёт и возвращает драйвер Firefox. Первоначально происходит
    попытка создания драйвера с использованием GeckoDriverManager из
    библиотеки webdriver_manager, в случае неуспешной попытки (на Linux c
    применением snap пакетов, создание объекта управления драйвером может
    потерпеть неудачу, т.к. snap пакет использует свой драйвер) функция
    попробует создать объект webdriver.Firefox на базе драйвера пакета snap,
    используя значения переданных параметров для отыскания установленных
    компонентов. (Работае только в случае, если в системе установлен snap
    пакет Firefox).
    :param binary_loc: путь к компоненту firefox
    :type binary_loc: str or None
    :param driver_loc: путь к компоненту geckodriver
    :type driver_loc: str
    :exception WebDriverException:
    :return:
    """
    opts = webdriver.FirefoxOptions()
    try:
        br_service = Service(GeckoDriverManager().install())
        return webdriver.Firefox(service=br_service, options=opts)
    except WebDriverException:
        print('GeckoDriverManager из webdriver_manager не запустился...')
    opts.binary_location = binary_loc
    return webdriver.Firefox(service=Service(driver_loc), options=opts)


def get_vk_redirect_uri(app_id: int, browser: webdriver.Firefox) -> str:
    """Возвращает строковое представление адрессной строки Вконтакте.

    Использую объект переданного webdriver-a, функция запускает процедуру
    регистрации Вконтакте, после её прохождения - функция переходит на
    указанную в запросе страницу, содержащую в адреснной строке токен
    и id пользователя. Эту строку функция и возвращает. (На регистрацию
    выделяется 180 сек).
    :param app_id: app_id Standalone-приложения
    :type app_id: int
    :param browser: объект WebDriver: Firefox, Chrome, Safari...
    :type browser: WebDriver
    :return:
    :exception WebDriverException:
    """
    url = ('https://oauth.vk.com/authorize'
           f'?client_id={app_id}'
           '&display=page&redirect_uri=https://oauth.vk.com/blank.html'
           '&scope=1030&response_type=token&v=5.191&state=123456')
    browser.get(url)
    try:
        WebDriverWait(browser, 180).until(
            ec.presence_of_element_located(
                (By.XPATH, '//body/b[1][text()="не копируйте"]')
            ),
            message='Превышено время ожидания авторицации...'
        )
        return browser.current_url
    finally:
        browser.quit()


def get_token_and_id(redirect_uri: str) -> tuple[str, str]:
    """Возвращает кортеж из токена и id пользователя Вконтакте

    На вход подаётся строковое представление адрессной строки страницы
    регистрации Вконтакте
    :param redirect_uri: адресная строка страницы переадресации при регистрации
    :return:
    """
    token = redirect_uri.split('=')[1].replace('&expires_in', '')
    user_id = redirect_uri.split('=')[3].replace('&state', '')
    return token, user_id


class Meths(StrEnum):
    USERS_GET = 'users.get'
    MESSAGES_SEND = 'messages.send'
    USER_SEARCH = 'users.search'
    MESSAGES_EDIT = 'messages.edit'


# class KeyWord(StrEnum):
#     ENOUGH = 'хватит'
#     FND_PEOPLE = 'найти Далёких странников'


class ActionInterface:

    def __init__(self):
        self.kb_is_act = False
        # self.prev_actions = {}
        # self.prev_kb = None
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


class User:
    """Класс, описывающий пользователя социальной сети Вконтакте.

    Класс на вход принимает один параметр - item, находящийяся, в ответе на
    запрос 'users.search', в поле 'items'.
    :param data: является словарeм, описывающим поля пользователя
    """

    DT_FORMAT = '%d.%m.%Y'

    def __init__(self, data: dict):
        self.id: int = data.get('id', 0)
        self.first_name: str = data.get('first_name', '')
        self.last_name: str = data.get('last_name', '')
        self.bdate: str = data.get('bdate', '')
        self.city_id: int | None = data.get('city', {}).get('id')
        self.city_title: str = data.get('city', {}).get('id')
        self.sex: int = data.get('sex', 0)
        self.have_access = data.get('can_access_closed', False)
        self.is_closed = data.get('is_closed', True)

    def get_age(self) -> int:
        birthday = datetime.strptime(self.bdate, self.DT_FORMAT)
        cur_day = datetime.now()
        y, m, d = birthday.year, cur_day.month, cur_day.day
        return cur_day.year - y - (birthday > datetime(y, m, d))
