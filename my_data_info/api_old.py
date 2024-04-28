import json
from random import randrange
from datetime import datetime

# import requests
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import vk_data as vdt


class MyApi(VkApi):

    def __init__(self, my_token='', my_user_id=0, my_version='5.191',
                 my_scope=1030):
        """Создаёт конструктор базового классо

        Ининциализирует переменные супер классф
        :param my_token: токен для реги
        :param my_user_id: ываывфа
        :param my_version: фывафыаф
        :param my_scope: ывфафывафыа
        """
        super().__init__(token=my_token, api_version=my_version,
                         scope=my_scope)
        self.user_id = my_user_id

    def get_get_user_info_2(self) -> None:
        params = {
            'user_ids': self.user_id,
            'fields': 'city,bdate,sex,interests'
        }
        response = self.method('users.get', params)
        print(response)


class CurrVkApi():
    BASE_VK_URL = 'https://api.vk.com/method/'

    def __init__(self, app_id: int, token='', user_id=0, version='5.191'):
        self.app_id = app_id
        self.token = token
        self.id = user_id
        self.first_name = ''
        self.last_name = ''
        self.sex = 0
        self.birthdate: datetime | None = None
        self.city = ''
        self.interests = ''
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.vkapi = VkApi(token=self.token,
                           scope=1030,
                           api_version=self.version)
        self._data_api_initialization()

    def get_users_info(self) -> json:
        url = f'{self.BASE_VK_URL}{self.USERS_GET}'
        some_params = {
            'user_ids': self.id,
            'fields': 'city,bdate,sex,interests'
        }
        response = requests.get(url, params={**self.params, **some_params})
        return response.json()

    def _data_api_initialization(self) -> None:
        user_data = self._check_token_and_id()['response'][0]
        self.first_name = user_data['first_name']
        self.last_name = user_data['last_name']
        if birthdate := user_data['bdate']:
            self.birthdate = datetime.strptime(birthdate, '%d.%m.%Y')
        if city := user_data['city']:
            self.city = city['title']
        if interests := user_data['interests']:
            self.interests = interests
        if sex := int(user_data['sex']):
            self.sex = sex

    def _check_token_and_id(self) -> dict:
        user_data = {'error': None}
        if self.token and self.id:
            user_data = self.get_users_info()
        if 'error' in user_data or not self.token or not self.id:
            browser = vdt.get_browser(*vdt.get_paths())
            redirect_uri = vdt.get_vk_redirect_uri(self.app_id, browser)
            self.token, self.id = vdt.get_token_and_id(redirect_uri)
            self.params['access_token'] = self.token
            print(f'Ваш новый токен: {self.token}')
            user_data = self.get_users_info()
        return user_data

    def get_get_user_info_2(self) -> None:
        params = {
            'user_ids': self.id,
            'fields': 'city,bdate,sex,interests'
        }
        response = self.vkapi.method(self.MESSAGES_SEND, params)
        print(response)

    def print_user_info(self) -> None:
        print('Данные пользователя:')
        print(f'{self.first_name=}, {self.last_name=}')
        print(f'{self.city=}, {self.interests=}, {self.id=}, {self.sex=}')
        print(self.birthdate.strftime('%d.%m.%Y'))


class VkBotAPI():

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
        self.vkapi.method(vdt.Meths.MESSAGES_SEND, values)

    def search_people(self):
        values = {
            'count': 5,
            'sex': 2,
            'age_from': 35,
            'age_to': 40,
            'has_photo': 1
        }
        self.vkapi.method(vdt.Meths.MESSAGES_SEND, values)

    def get_person_info(self):
        value = {
            'user_ids': [174200552, 465632516],
            'fields': ['city']
        }
        self.vkapi.method(vdt.Meths.USERS_GET, value)

    def get_person_photos(self):
        pass

    def get_id_list_of_people(self):
        pass

    def exit_from_vkbot(self, user_id):
        self.hide_keyboard(user_id, 'Убил...')
        exit(0)
