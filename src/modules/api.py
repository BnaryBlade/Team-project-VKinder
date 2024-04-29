import sys
from random import randrange
from datetime import datetime, date
import traceback

from selenium.common.exceptions import WebDriverException
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
        self.city = {}
        self.interests = ''
        self._data_api_initialization()
        self.search_params = {'sex': self.sex,
                              'age_from': 30,
                              'age_to': 35,
                              'has_photo': 1}
        self.fields = 'city,sex,bdate'

    def _data_api_initialization(self) -> None:
        try:
            user_data = self._check_token_and_id()[0]
        except (WebDriverException, ApiError):
            traceback.print_exc()
            print('Не выполнена авторизация пользователя в UserVkApi...')
            sys.exit(1)
        else:
            self.first_name = user_data['first_name']
            self.last_name = user_data['last_name']
            if birthdate := user_data['bdate']:
                self.birthdate = birthdate
            if city := user_data['city']:
                self.city = city
            if interests := user_data['interests']:
                self.interests = interests
            if sex := int(user_data['sex']):
                self.sex = sex

    def _check_token_and_id(self) -> dict:
        """Проверяет токен и id пользователя.

        Проверяет наличие и актуальност токена и id пользователя спомощью
        запроса на получение данных пользователя, если запрос выдаёт
        исключение, метод пробует произвести авторизацию пользователя.
        :exception WebDriverException
        :exception ApiError
        :return:
        """
        if self.token is not None and self.user_id is not None:
            try:
                return self.get_user_info()
            except ApiError as e:
                print(e)
        browser = vdt.get_browser(*vdt.get_paths())
        redirect_uri = vdt.get_vk_redirect_uri(self.app_id, browser)
        token, user_id = vdt.get_token_and_id(redirect_uri)
        self.token = {'access_token': token}
        self.user_id = user_id
        print(f'Ваш новый токен: {token}')
        return self.get_user_info()

    def get_user_info(self) -> dict:
        """Метод возвращает данные пользователя по его id.
        :exception ApiError:
        :return:
        """
        params = {
            'user_ids': self.user_id,
            'fields': 'city,bdate,sex,interests'
        }
        return self.method(vdt.Meths.USERS_GET, params)

    def search_users(self, count: int) -> list | None:
        params = {'count': count, **self.search_params, 'fields': self.fields}
        return self.method(vdt.Meths.USER_SEARCH, params)


class BotVkApi(VkApi):

    def __init__(self, group_token: str, api_version: str = '5.191',
                 app_id: int = 6222115) -> None:
        super().__init__(token=group_token, app_id=app_id,
                         api_version=api_version)
        self.keyboard: VkKeyboard = vdt.get_dialog_keyboard()
        # self.b_is_active = False
        self.id_list_of_people = {}

    def show_keyboard(self, user_id: int, message: str,
                      kb: VkKeyboard) -> bool:
        try:
            self.write_msg(user_id, message, keyboard=kb.get_keyboard())
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
