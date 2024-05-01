import vk_api
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
token = os.getenv('my_token')
session = vk_api.VkApi(token=token)
user_id_VK = os.getenv('user_id_VK')


def data_user_VK(user_id):
    data = session.method("users.get", {"user_ids": user_id,
                                        "fields": "id, first_name, _name, city, sex, bdate",
                                        })
    return data[0]


def data_users(sex, id_city):
    sex = sex
    id_city = id_city
    data_users = session.method("users.search", {
        'sex': sex,
        'city': id_city,
        'is_closed': 'False',
        'count': '5',
        'fields': "city, sex, bdate",
        'has_photo': '1',
        'sort': '0',
    })
    list = data_users['items']
    users_list_new = []

    for index, valeu in enumerate(list):
        users_list_new_2 = {}
        if (valeu['is_closed'] == True) or \
                ('city' not in valeu) or \
                ('bdate' not in valeu):
            continue
        else:
            users_list_new_2 = dict(first_name=valeu['first_name'],
                                    last_name=valeu['last_name'],
                                    bdate=valeu['bdate'],
                                    sex=valeu['sex'],
                                    city=valeu['city'],
                                    id=valeu['id'])
            users_list_new.append(users_list_new_2)

    # print(users_list_new)
    # print(len(users_list_new))

    return users_list_new


def upload_photos(id_user):
    """Функция находит фотографии в профиле пользователя по id и возвращает список в формате photoХХХХ_УУУУ"""
    def_URL = session.method("photos.get", {
        'owner_id': id_user,
        'album_id': 'profile',
        'extended': '1',
    })
    """Сортировка фотографий пользователя по количеству лайков"""
    if def_URL['count'] == 0:
        photo_list = []
    elif def_URL['count'] <= 3:  # если у пользовотеля меньше 3 фотографий получаем имеющиеся
        photo_list = [f"{iter_['sizes'][-1]['url']}" for iter_ in def_URL['items']]
    else:  # если у пользовотеля больше 3 фотографий получаем имеющиеся
        dict_photo_likes = {f"{iter_['sizes'][-1]['url']}": iter_['likes']['count'] for iter_ in def_URL['items']}
        sort_dict_photo_likes = sorted(dict_photo_likes, key=dict_photo_likes.get, reverse=True)[:3]
        photo_list = [f"{iter_}" for iter_ in sort_dict_photo_likes]
    return photo_list


data = data_user_VK(user_id_VK)

# default
sex = 0
id_city = data['city']['id']
# default

foto = data_users(sex, id_city)
print('можно отсюда в бд затягивать = ', len(foto), 'длина списка факт')
print(foto)  # можно отсюда в бд затягивать
users_photos_new = []
for index, valeu in enumerate(foto):
    id_foto = foto[index]['id']
    url = upload_photos(id_foto)
    # print(url)
    photos = dict(vk_id=foto[index]['id'], photo_link=url)
    users_photos_new.append(photos)  # можно отсюда в бд затягивать
print()
print('список словарей id: photo_link  = ', len(users_photos_new), 'длина списка факт')

print(users_photos_new)
