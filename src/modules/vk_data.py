import os
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


class ActionInterface:

    def __init__(self):
        self.kb_is_act = False
        self.curr_action = {}
        self.curr_kb = None

    def _get_start_dialog_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button('найти Далёких странников',
                            VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('хватит', VkKeyboardColor.PRIMARY)
        key_word = {'найти Далёких странников': self._go_choose_view_options,
                    'exit': self._exit_from_vkbot,
                    'хватит': self._stop_bot_dialog}
        return keyboard, key_word

    def _get_choosing_actions_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button('найти новых людей', VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('показать людей из черного списка',
                            VkKeyboardColor.POSITIVE)
        keyboard.add_button('показать избранных', VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('очистить историю просмотра',
                            VkKeyboardColor.POSITIVE)
        keyboard.add_button('очистить черный список',
                            VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('хватит', VkKeyboardColor.POSITIVE)
        key_word = {
            'найти новых людей': self._go_search_people,
            'показать людей из черного списка': self._go_blacklist_view,
            'показать избранных': self._go_favorites_view,
            'очистить историю просмотра': self._clear_history,
            'очистить черный список': self._clear_blacklist,
            'exit': self._exit_from_vkbot,
            'хватит': self._stop_bot_dialog
        }
        return keyboard, key_word

    def _get_criteria_selection_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button('город', VkKeyboardColor.SECONDARY)
        keyboard.add_button('возраст', VkKeyboardColor.SECONDARY)
        keyboard.add_button('пол', VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('интересы', VkKeyboardColor.POSITIVE)
        keyboard.add_button('резерв №1', VkKeyboardColor.POSITIVE)
        keyboard.add_button('резерв №2', VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('показывай', VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('назад', VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('хватит', VkKeyboardColor.POSITIVE)
        key_word = {'назад': self._come_back,
                    'город': self._choose_city,
                    'возраст': self._choose_age,
                    'пол': self._choose_sex,
                    'интересы': self._choose_sex,
                    'резерв №1': self._choose_reserve_1,
                    'резерв №2': self._choose_reserve_2,
                    'показывай': self._go_browsing,
                    'exit': self._exit_from_vkbot,
                    'хватит': self._stop_bot_dialog}
        return keyboard, key_word

    def _get_queue_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button('не интересно', VkKeyboardColor.SECONDARY)
        keyboard.add_button('интересно', VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('следующий', VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('назад', VkKeyboardColor.PRIMARY)
        keyboard.add_button('хватит', VkKeyboardColor.PRIMARY)
        key_word = {'не интересно': self._add_to_blacklist,
                    'интересно': self._add_to_favorites,
                    'следующий': self._show_next_user,
                    'назад': self._come_back,
                    'exit': self._exit_from_vkbot,
                    'хватит': self._stop_bot_dialog}
        return keyboard, key_word

    def _get_viewing_history_kb(self) -> tuple[VkKeyboard, dict]:
        keyboard = VkKeyboard()
        keyboard.add_button('предыдущий', VkKeyboardColor.SECONDARY)
        keyboard.add_button('cледующий', VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('назад', VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('хватит', VkKeyboardColor.POSITIVE)
        key_word = {'cледующий': self._show_next_user,
                    'предыдущий': self._show_previous_user,
                    'назад': self._come_back,
                    'exit': self._exit_from_vkbot,
                    'хватит': self._stop_bot_dialog}
        return keyboard, key_word

    # Реализация комыды "exit" и кнопки "хватит", общих для всего интерфейса
    def _exit_from_vkbot(self):
        pass

    def _stop_bot_dialog(self):
        pass

    # Реализация интерфейса стартовой клавиатуры
    def _start_bot_dialog(self):
        pass

    def _go_choose_view_options(self):
        pass

    # Реализация клавиатуры выбора вариантов просмотра пользователей
    def _go_search_people(self):
        pass

    def _go_blacklist_view(self):
        pass

    def _go_favorites_view(self):
        pass

    def _clear_history(self):
        pass

    def _clear_blacklist(self):
        pass

    # Реализация клавиатуры выбора опций поиска новых лидей
    def _choose_city(self):
        pass

    def _choose_age(self):
        pass

    def _choose_sex(self):
        pass

    def _choose_reserve_1(self):
        pass

    def _choose_reserve_2(self):
        pass

    def _go_browsing(self):
        pass

    # Реализация клавивтуры просмотра новых пользователей
    def _add_to_blacklist(self):
        pass

    def _add_to_favorites(self):
        pass

    # Реализация кнопки "предыдущий" клвавиатуры просмотра избранных
    def _show_previous_user(self):
        pass

    # Реализация кнопки "назад" и "следующий" общей для нескольких клавиатур
    def _come_back(self):
        pass

    def _show_next_user(self):
        pass


class Meths(StrEnum):
    USERS_GET = 'users.get'
    MESSAGES_SEND = 'messages.send'
    USER_SEARCH = 'users.search'


class User:

    def __init__(self, user_id):
        self.id = user_id
