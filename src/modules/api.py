import os
from random import randrange

from vk_api import VkApi
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class User:

    def __init__(self, name, surname, vk_id):
        self.first_name = name
        self.last_name = surname
        self.vk_id = vk_id


class VKBot:

    def __init__(self, api: VkApi) -> None:
        self.vkapi = api
        self._initializing_keyboard()
        self.is_active = False

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

    def exit_from_vkbot(self, user_id):
        self.hide_keyboard(user_id, 'Убил...')
        exit(0)
