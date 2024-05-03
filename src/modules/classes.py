from api import UserVkApi
from vk_data import Photo, User


class Criteria:
    MIN_AGE = 1
    MAX_AGE = 120
    STR_SEX = {0: 'не важен', 1: 'женский', 2: 'мужской'}

    def __init__(self):
        self.age_from = self.MIN_AGE
        self.age_to = self.MAX_AGE
        self.sex = 0
        self.city_id = 0
        self.city_title = ''
        self.is_criteria_changed = False
        self.offset = 0

    def check_user(self, user: User) -> bool:
        return all([self.check_sex(user.sex),
                    self.check_user_age(user.get_age()),
                    self.check_user_city(user.city_id)])

    def check_user_age(self, age: int) -> bool:
        return self.age_from <= age <= self.age_to

    def check_user_city(self, city_id: int) -> bool:
        return city_id == self.city_id

    def check_sex(self, sex: int) -> bool:
        return True if not self.sex else sex == self.sex

    def set_criteria_from_user(self, user: User) -> None:
        self.age_from = user.get_age()
        self.age_to = user.get_age()
        self.sex = user.sex if user.sex else 0
        self.city_id = user.city_id
        self.city_title = user.city_title

    def get_descr_criteria(self) -> str:
        str_sex = self.STR_SEX.get(self.sex, 'неважен')
        text = (
            f'''
            Критерии поиска:
            - возраст: от {self.age_from} до {self.age_to} лет;
            - пол: {str_sex};
            - город: {self.city_title}.
            '''
        )
        return text

    def get_search_params(self) -> dict:
        search_params = {'sex': self.sex,
                         'city_id': self.city_id,
                         'age_from': self.age_from,
                         'age_to': self.age_to,
                         'has_photo': 1,
                         'fields': 'city,sex,bdate',
                         'offset': self.offset}
        return search_params


class SearchEngine(Criteria):
    STEP_SEARCH = 10

    def __init__(self, user_token: str = None, user_id: int | str = None):
        super().__init__()
        self.api = UserVkApi(token=user_token, user_id=user_id)
        self.is_search_going_on = False
        self.user_list = []

    def get_data_users(self) -> bool:
        params = self.get_search_params()
        if users_data := self.api.search_users(params):
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

    def start_found_users(self) -> User | None:
        self.is_search_going_on = True
        return self.get_next_user()

    def stop_found_users(self):
        self.is_search_going_on = False
        self.offset = 0
        self.user_list.clear()

    def get_next_user(self) -> User | None:
        if self.user_list:
            return self.user_list.pop(0)
        else:
            self.get_data_users()
            try:
                return self.user_list.pop(0)
            except IndexError:
                print('Всё!!! Смотреть больше некого...')
                return None

    def search_city(self, city_name: str, count=1) -> list[dict]:
        return self.api.get_city(city_name, count)
