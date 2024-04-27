import json
import os
from random import randrange

import requests
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import WebDriverException


def get_paths() -> tuple[str, str]:
    install_dir = '/snap/firefox/current/usr/lib/firefox'
    driver_loc = os.path.join(install_dir, "geckodriver")
    binary_loc = os.path.join(install_dir, "firefox")
    return binary_loc, driver_loc


def get_browser() -> webdriver.Firefox:
    opts = webdriver.FirefoxOptions()
    try:
        br_service = Service(GeckoDriverManager().install())
        return webdriver.Firefox(service=br_service, options=opts)
    except WebDriverException:
        print('GeckoDriverManager из webdriver_manager не запустился...')
    opts.binary_location, driver_loc = get_paths()
    return webdriver.Firefox(service=Service(driver_loc), options=opts)


class User:

    def __init__(self, name, surname, vk_id):
        self.first_name: str = name
        self.last_name = surname
        self.vk_id: int = vk_id
        self.city: str | None = None
        self.is_favorite = False
        self.photos = {}

    def get_user_data(self) -> json:
        user_data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'vk_id': self.vk_id
        }
        return json.dumps(user_data)


class CurrVkApi:

    def __init__(self,
                 access_token: str | None = None,
                 user_id: int | None = None,
                 version='5.191'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.browser = get_browser()

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_requests(self):
        self.browser.get('https://google.com')
        self.browser.quit()

    def get_token(self):
        url = (f'https://oauth.vk.com/authorize'
               f'?client_id=51914485'
               f'&display=page&redirect_uri=http://example.com/callback'
               f'&scope=6&response_type=token&v=5.191&state=123456')
        self.browser.get(url)


class VkBotAPI:

    def __init__(self, some_api: VkApi) -> None:
        self.vkapi = some_api
        self._initializing_keyboard()
        self.is_active = False
        self.id_list_of_people = {}

    def _initializing_keyboard(self) -> None:
        self.keyboard = VkKeyboard()
        self.keyboard.add_button('следующий', VkKeyboardColor.SECONDARY)
        self.keyboard.add_button('покажи выбраных', VkKeyboardColor.POSITIVE)
        self.keyboard.add_button('предыдущий', VkKeyboardColor.SECONDARY)
        self.keyboard.add_line()
        self.keyboard.add_button('не интересно', VkKeyboardColor.NEGATIVE)
        self.keyboard.add_button('ИНТЕРЕСНО', VkKeyboardColor.POSITIVE)
        self.keyboard.add_line()
        self.keyboard.add_button('хватит', VkKeyboardColor.PRIMARY)

    def show_keyboard(self, user_id: int) -> None:
        if not self.is_active:
            self.write_msg(user_id,
                           'А вот и Я...',
                           self.keyboard.get_keyboard())
            self.is_active = True

    def hide_keyboard(self, user_id: int,
                      message='Мне пора, счастливо!!!') -> None:
        self.write_msg(user_id, message, self.keyboard.get_empty_keyboard())
        self.is_active = False

    def write_msg(self, user_id: int,
                  message: str,
                  keyboard: str = '',
                  random_id=False) -> None:
        message_id = randrange(10 ** 7) if random_id else 0
        values = {
            'user_id': user_id,
            'message': message,
            'random_id': message_id
        }
        if keyboard:
            values.update({'keyboard': keyboard})
        self.vkapi.method('messages.send', values)

    def search_people(self):
        values = {
            'count': 5,
            'sex': 2,
            'age_from': 35,
            'age_to': 40,
            'has_photo': 1
        }
        self.vkapi.method('users.search', values)

    def get_person_info(self):
        value = {
            'user_ids': [174200552, 465632516],
            'fields': ['city']
        }
        self.vkapi.method('users.get', value)

    def get_person_photos(self):
        pass

    def get_id_list_of_people(self):
        pass

    def exit_from_vkbot(self, user_id):
        self.hide_keyboard(user_id, 'Убил...')
        exit(0)


if __name__ == '__main__':
    api = CurrVkApi()
# try:
#     driver_path = GeckoDriverManager().install()
#     firefox_service = Service(executable_path=driver_path)
#     opts = webdriver.FirefoxOptions()
#     browser = webdriver.Firefox(service=firefox_service, options=opts)
# except WebDriverException:
#     print('GeckoDriverManager из webdriver_manager не запустился...')
#     browser = None
# if browser is None:
#     install_dir = '/snap/firefox/current/usr/lib/firefox'
#     driver_loc = os.path.join(install_dir, "geckodriver")
#     binary_loc = os.path.join(install_dir, "firefox")
#     service = Service(driver_loc)
#     opts = webdriver.FirefoxOptions()
#     opts.binary_location = binary_loc
#     browser = webdriver.Firefox(service=service, options=opts)

# firefox_options = webdriver.FirefoxOptions()
# firefox_options.binary_location = "/usr/bin/firefox"
#
# s = Service("config/geckodriver")
# driver = webdriver.Firefox(options=firefox_options, service=s)

# service_my = GeckoDriverManager().install()
# print()
# print(service_my)
# print()
# option = Options()
# with open('log_file.txt', 'w', encoding='utf=8') as f:
#     br_service = Service(executable_path=service_my, log_output=f)
#     driver = Firefox(service=br_service, options=option)
#     driver.get('https://google.com')
# # waiting_driver = WebDriverWait(driver, timeout=10)
