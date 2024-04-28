from random import randrange
# from datetime import datetime
import traceback

from vk_api import VkApi
from vk_api.exceptions import ApiError
from vk_api.keyboard import VkKeyboard

import vk_data as vdt


class UserVkApi(VkApi):
    DATE_FORMAT = '%d.%m.%Y'

    def __init__(self, login: str = None,
                 password: str = None,
                 token: str = None,
                 user_id: int = None,
                 api_version: str = '5.191',
                 app_id: int = 6222115) -> None:
        super().__init__(login=login, password=password, token=token,
                         app_id=app_id, api_version=api_version)
        self.user_id = user_id
        self.first_name = ''
        self.last_name = ''
        self.sex = 0
        self.birthdate = ''
        self.city = ''
        self.interests = ''
        self._data_api_initialization()

    def _data_api_initialization(self) -> None:
        user_data = self._check_token_and_id()
        if user_data is None:
            print('Не получилось загрузить данные пользователя...')
            return None
        self.first_name = user_data['first_name']
        self.last_name = user_data['last_name']
        if birthdate := user_data['bdate']:
            self.birthdate = birthdate
        if city := user_data['city']:
            self.city = city['title']
        if interests := user_data['interests']:
            self.interests = interests
        if sex := int(user_data['sex']):
            self.sex = sex

    def _check_token_and_id(self) -> dict | None:
        if self.token is not None and self.user_id is not None:
            try:
                user_data = self.get_user_info()
                return user_data[0] if user_data is not None else None
            except ApiError:
                traceback.print_exc()
        browser = vdt.get_browser(*vdt.get_paths())
        if browser is not None:
            redirect_uri = vdt.get_vk_redirect_uri(self.app_id, browser)
            if redirect_uri is not None:
                token, user_id = vdt.get_token_and_id(redirect_uri)
                self.token = {'access_token': token}
                self.user_id = user_id
                print(f'Ваш новый токен: {token}')
                user_data = self.get_user_info()
                return user_data[0] if user_data is not None else None
        return None

    def get_user_info(self) -> list | None:
        params = {
            'user_ids': self.user_id,
            'fields': 'city,bdate,sex,interests'
        }
        try:
            response = self.method(vdt.Meths.USERS_GET, params)
            return response
        except ApiError:
            traceback.print_exc()
            return None

    def search_users(self, count: int) -> list | None:
        params = {'count': 5, 'sex': 2, 'age_from': 35, 'age_to': 40,
                  'has_photo': 1}
        try:
            response = self.method(vdt.Meths.USER_SEARCH, params)
            return response
        except ApiError:
            traceback.print_exc()
            return None

    def print_user_info(self) -> None:
        print('Данные пользователя:')
        print(f'{self.first_name=}, {self.last_name=}')
        print(f'{self.city=}, {self.interests=}, {self.user_id=}, {self.sex=}')
        print(self.birthdate)


class BotVkApi(VkApi):

    def __init__(self, group_token: str, api_version: str = '5.191',
                 app_id: int = 6222115) -> None:
        super().__init__(token=group_token, app_id=app_id,
                         api_version=api_version)
        self.keyboard: VkKeyboard = vdt.get_dialog_keyboard()
        # self.b_is_active = False
        self.id_list_of_people = {}

    def show_keyboard(self, user_id: int) -> bool:
        try:
            self.write_msg(user_id, 'А вот и Я...',
                           self.keyboard.get_keyboard())
            return True
        except ApiError:
            traceback.print_exc()
            return False

    def hide_keyboard(self, user_id: int,
                      message='Мне пора, счастливо!!!') -> bool:
        try:
            self.write_msg(user_id, message,
                           self.keyboard.get_empty_keyboard())
            return True
        except ApiError:
            traceback.print_exc()
            return False

    def write_msg(self, user_id: int, message: str, keyboard: str = '',
                  random_id=False) -> bool:
        message_id = randrange(10 ** 7) if random_id else 0
        values = {'user_id': user_id,
                  'message': message,
                  'random_id': message_id}
        if keyboard:
            values.update({'keyboard': keyboard})
        try:
            self.method(vdt.Meths.MESSAGES_SEND, values)
            return True
        except ApiError:
            traceback.print_exc()
            return False
