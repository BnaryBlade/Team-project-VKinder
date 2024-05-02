from random import randrange
import traceback

# from selenium.common.exceptions import WebDriverException
from vk_api import VkApi
from vk_api.exceptions import ApiError

from additional_data import perform_authorization
from vk_data import User, Meths


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
        # self.user_id = user_id
        self.client = User({'id': user_id})
        self._uploading_client_data()
        self.search_params = {'sex': self.client.sex,
                              'age_from': 30,
                              'age_to': 35,
                              'has_photo': 1}
        self.fields = 'city,sex,bdate'

    def _uploading_client_data(self) -> None:
        """Загружеет данные пользователя-клиента.

        Проверяет наличие и актуальност токена и id пользователя с помощью
        запроса на получение его данных, при неуспешной загрузке данных,
        выполняет авторизацию пользователя с последующей повторной попыткой
        загрузки данных клиента.
        :exception WebDriverException
        :exception ApiError
        :return:
        """
        if client_data := self.get_users_info([self.client.id]):
            self.client.update_user_data(client_data[0])
        else:
            token, user_id = perform_authorization(self.app_id)
            print(f'Ваш новый токен: {token}')
            self.token = {'access_token': token}
            self.client.id = user_id
            if client_data := self.get_users_info([self.client.id]):
                self.client.update_user_data(client_data[0])

    def get_users_info(self, user_ids: list[int] = None) -> list[dict]:
        """Метод возвращает данные пользователя по его id.
        :exception ApiError:
        :return:
        """
        if user_ids is not None:
            user_ids = ','.join(map(str, user_ids))
        params = {
            'user_ids': user_ids,
            'fields': 'city,bdate,sex,interests'
        }
        try:
            if response := self.method(Meths.USERS_GET, params):
                return response
            else:
                return []
        except ApiError:
            traceback.print_exc()
            print('Не получилось загрузить данные пользователей...')
            return []

    def search_users(self, count: int, params: dict,
                     fields='', offset=0) -> list[dict]:
        params['count'] = count
        params['fields'] = ','.join([params.get('fields', ''), fields])
        params['offset'] = offset
        try:
            return self.method(Meths.USER_SEARCH, params).get('items', [])
        except ApiError:
            traceback.print_exc()
            print('Не получилось загрузить список пользователей...')
            return []

    def get_user_photos(self, user_id: int) -> list[dict]:
        params = {'owner_id': user_id, 'album_id': 'profile', 'extended': '1'}
        try:
            return self.method(Meths.PHOTOS_GET, params).get('items', [])
        except ApiError:
            traceback.print_exc()
            print('Не получилось загрузить список фото пользователей...')
            return []


class BotVkApi(VkApi):

    def __init__(self, group_token: str, api_version: str = '5.191',
                 app_id: int = 6222115) -> None:
        super().__init__(token=group_token, app_id=app_id,
                         api_version=api_version)
        self.id_list_of_people = {}

    def show_kb(self, user_id: int, message: str, kb='') -> bool:
        if self._send_msg(user_id, message, kb):
            return True
        else:
            print('Не получилось отообразить клавиатуру...')
            return False

    def hide_kb(self, user_id: int, message: str, kb='') -> bool:
        if self._send_msg(user_id, message, kb):
            return True
        else:
            print('Не получилось отключить клавиатуру...')
            return False

    def write_msg(self, user_id: int, message: str) -> bool:
        return self._send_msg(user_id, message)

    def _send_msg(self, user_id: int, message='', kb='', r_id=False) -> bool:
        random_id = randrange(10 ** 7) if r_id else 0
        values = {'user_id': user_id,
                  'message': message,
                  'random_id': random_id,
                  'keyboard': kb}
        try:
            self.method(Meths.MESSAGES_SEND, values)
            return True
        except ApiError:
            traceback.print_exc()
            print('Не получилось отпарвить сообщение...')
            return False

    def send_attachment(self, user_id: int, attachment='', r_id=True):
        random_id = randrange(10 ** 7) if r_id else 0
        values = {'user_id': user_id,
                  'random_id': random_id,
                  'attachment': attachment}
        try:
            self.method(Meths.MESSAGES_SEND, values)
            return True
        except ApiError:
            traceback.print_exc()
            print('Не получилось отпарвить фото...')
            return False
