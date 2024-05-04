from enum import IntEnum, StrEnum


class DftSrcCriteria(IntEnum):
    MIN_AGE = 1
    MAX_AGE = 120
    STEP_SEARCH = 10


class Meths(StrEnum):
    USERS_GET = 'users.get'
    MESSAGES_SEND = 'messages.send'
    USER_SEARCH = 'users.search'
    PHOTOS_GET = 'photos.get'
    GET_CITY = 'database.getCities'


class KeyWord(StrEnum):
    START_BOT = 'bot'
    STOP_USER_BOT = 'хватит'
    EXIT_FROM_BOT = 'exit'
    COME_BACK = 'назад'
    FND_PEOPLE = 'найти Далёких странников'
    FND_NEW_PEOPLE = 'найти новых людей'
    SHOW_FAVORITES = 'показать избранных'
    SHOW_BLACKLIST = 'показать неинтересных'
    CLEAR_BLACKLIST = 'очистить черный список'
    CLEAR_HISTORY = 'очистить список избранных'
    CHOOSE_AGE = 'выбрать возраст'
    CHOOSE_CITY = 'выбрать город'
    CHOOSE_SEX = 'выбрать пол'
    LETS_SHOW = 'показывай'
    NEXT_USER = 'покажи ещё одного...'
    IS_INTERESTING = 'интересно'
    IS_NOT_INTERESTING = 'не интересно'
    PREVIOUS_PERSON = 'предыдущий'
    DELETE_FROM_LIST = 'удалить из списка'
    NEXT_PERSON = 'следующий'
