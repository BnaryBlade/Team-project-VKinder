from random import randrange

import requests
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from data import get_token


class CurrVkApi:

    def __init__(self,
                 app_id: str,
                 access_token: str | None = None,
                 user_id: int | None = None,
                 version='5.191'):
        self.app_id = app_id
        self.token = get_token(access_token, self.app_id)
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_requests(self):
        self.browser.get('https://google.com')
        self.browser.quit()


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
