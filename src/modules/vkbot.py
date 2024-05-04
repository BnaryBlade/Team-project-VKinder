import os

from vk_api.longpoll import VkLongPoll, VkEventType

from db import ModelDb
from classes import UserBot, GropVkApi, UserVkApi, User, KeyWord


class Bot:

    def __init__(self, admin_id: int, admin_token: str, group_token: str,
                 db_login: str, db_password: str, db_name='vk_bot_db') -> None:
        self.u_api = UserVkApi(token=admin_token, user_id=admin_id)
        self.api = GropVkApi(group_token=group_token)
        self.database = ModelDb(login=db_login, password=db_password,
                                db_name=db_name)
        self.user_bots: dict[UserBot] | dict = {}

    def launching_bot(self):
        for event in VkLongPoll(self.api).listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    if (event.user_id == self.u_api.admin.id
                            and event.text == KeyWord.EXIT_FROM_BOT):
                        self.stop_user_bots()
                        break
                    if event.user_id in self.user_bots:
                        bot = self.user_bots.get(event.user_id)
                        if isinstance(bot, UserBot):
                            if event.text.strip() == KeyWord.STOP_USER_BOT:
                                bot.stop_bot_dialog()
                                self.user_bots.pop(event.user_id)
                            else:
                                bot.event_handling(event)
                    else:
                        if event.text.lower().strip() == KeyWord.START_BOT:
                            client = User(
                                self.u_api.get_users_info([event.user_id])[0]
                            )
                            bot = UserBot(user_api=self.u_api,
                                          user=client,
                                          bot_api=self.api,
                                          model_db=self.database)
                            message = 'Я снова с Вами... :-)'
                            bot.start_bot_dialog(message)
                            self.user_bots[event.user_id] = bot

    def stop_user_bots(self):
        message = 'Админ меня убил... :-('
        for _, bot in self.user_bots.items():
            bot.stop_bot_dialog(message)


if __name__ == '__main__':
    login_db = os.environ['LOGIN_DB']
    password_db = os.environ['PASSWORD_DB']

    my_group_token = os.environ['MY_GROUP_TOKEN']
    # grp_token = os.environ['GROUP_TOKEN']
    my_token = os.environ['TOKEN']
    my_id = int(os.environ['USER_ID'])
    main_bot = Bot(my_id, my_token, my_group_token, login_db, password_db)
    main_bot.launching_bot()
