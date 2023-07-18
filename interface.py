# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import comunity_token, acces_token, db_url_object
from core import VkTools
from data_store import Base, add_user, check_user



# отправка сообщений
class BotInterface():
    def __init__(self, comunity_token, acces_token):
        self.vk = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(acces_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                       {'user_id': user_id,
                        'message': message,
                        'attachment': attachment,
                        'random_id': get_random_id()}
                       )

# обработка событий / получение сообщений

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                interaction = event.text.lower()
                if interaction == 'привет':

                    '''Логика для получения данных о пользователе'''
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Привет, {self.params["name"]}, я бот для знакомств, для того чтобы найти собеседника введите "поиск"')

                    if self.params.get('city') is None:
                        self.params['city'] = self.city_add(event.user_id)
                    if self.params.get('bdate') is None:
                        self.params['bdate'] = self.bdate_add(event.user_id)

                elif interaction == 'поиск':
                    '''Логика для поиска анкет'''
                    self.message_send(event.user_id, 'Идёт поиск')

                    if self.worksheets:
                        worksheet = self.worksheets.pop()
                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'

                    else:
                        self.worksheets = self.vk_tools.search_worksheet(
                            self.params, self.offset)

                        worksheet = self.worksheets.pop()
                        'првоерка анкеты в бд в соотвествие с event.user_id'

                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                        self.offset += 10

                    self.message_send(
                        event.user_id,
                        f'имя: {worksheet["name"]} ссылка: vk.com/{worksheet["id"]}',
                        attachment=photo_string
                    )

                    'добавить анкету в бд в соотвествие с event.user_id'

                elif interaction == 'пока':
                    self.message_send(
                        event.user_id, 'До свидания')
                else:
                    self.message_send(
                        event.user_id, 'Неизвестная команда')

    def city_add(self, user_id):
        self.message_send(user_id, 'Укажите название города и введите "поиск"')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                return event.text

    def bdate_add(self, user_id):
        self.message_send(user_id, 'Укажите дату рождения: дд.мм.ггг и введите "поиск"')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                return event.text

    def get_profile(self, worksheets, event):
        while True:
            if worksheets:
                worksheet = worksheets.pop()
                if not check_user(engine, event.user_id, worksheet['id']):
                    add_user(engine, event.user_id, worksheet['id'])
                    yield worksheet
            else:
                worksheets = self.vk_tools.search_worksheet(
                    self.params, self.offset)



if __name__ == '__main__':
    bot_interface = BotInterface(comunity_token, acces_token)
    bot_interface.event_handler()