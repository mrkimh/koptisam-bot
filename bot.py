import config
import telebot
from telebot import types
from string import Template

bot = telebot.TeleBot(config.token)
user_dict = {}


class User:
    def __init__(self, size):
        self.city = size

        keys = ['fullname', 'phone', 'driverSeria', 'driverNumber', 'driverDate', 'car', 'carModel']

        for key in keys:
            self.key = None


def error_message(message):
    bot.reply_to(message, config.exception_message)
    bot.send_message(message.chat.id, '/start')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    # markup = types.InlineKeyboardMarkup()
    # key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    # key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    # markup.add(key_yes, key_no)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    order_btn = types.KeyboardButton(config.button_order)
    info_btn = types.KeyboardButton(config.button_more)
    contacts_btn = types.KeyboardButton(config.button_contact)
    markup.add(order_btn, info_btn, contacts_btn)

    bot.send_message(message.chat.id, config.welcome_message, reply_markup=markup)


# бот отвечает на текстовые сообщения и кнопки types.KeyboardButton
@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == config.button_order:
        order_step(message)
    elif message.text == config.button_more:
        bot.send_message(message.chat.id, config.description_message)
    elif message.text == config.button_contact:
        bot.send_message(message.chat.id, config.contacts_message)
    else:
        bot.send_message(message.chat.id, config.dont_know_message)


# бот отвечает на инлайн кнопки types.InlineKeyboardButton
# @bot.callback_query_handler(func=lambda call: True)
# def callback_worker(call):
#     if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
#         # код сохранения данных, или их обработки
#         bot.send_message(call.message.chat.id, 'да')
#     elif call.data == "no":
#         bot.send_message(call.message.chat.id, 'нет')


def order_step(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    small_btn = types.KeyboardButton(f'Маленькая - {config.small_price} грн')
    small_btn_thermo = types.KeyboardButton(f'Маленькая с термометром - {config.small_price_thermo} грн')
    big_btn = types.KeyboardButton(f'Большая - {config.big_price} грн')
    big_btn_thermo = types.KeyboardButton(f'Большая с термометром - {config.big_price_thermo} грн')
    markup.add(small_btn, small_btn_thermo)
    markup.add(big_btn, big_btn_thermo)
# TODO сделать выбор кол-ва для заказа
    msg = bot.send_message(message.chat.id, config.choose_goods_message, reply_markup=markup)
    bot.register_next_step_handler(msg, process_size_step)


def process_size_step(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = User(message.text)

        # удалить старую клавиатуру
        markup = types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(chat_id, config.full_name_message, reply_markup=markup)
        bot.register_next_step_handler(msg, process_fullname_step)
    except Exception:
        error_message(message)


def process_fullname_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.fullname = message.text

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
        markup.add(button_phone)

        msg = bot.send_message(chat_id, config.phone_message, reply_markup=markup)
        bot.register_next_step_handler(msg, process_phone_step)
    except Exception:
        error_message(message)


def process_phone_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        try:
            # если телефон передали кнопкой
            user.phone = message.contact.phone_number
        except AttributeError:
            # если телефон передали сообщением
            user.phone = message.text

        msg = bot.send_message(chat_id, config.city_message)
        bot.register_next_step_handler(msg, process_city_step)
    except Exception:
        error_message(message)


def process_city_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.driverNumber = message.text

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for item in config.delivery_company:
            markup.add(types.KeyboardButton(item))

        msg = bot.send_message(chat_id, config.choose_delivery_message, reply_markup=markup)
        bot.register_next_step_handler(msg, process_delivery_company_step)
    except Exception:
        error_message(message)


def process_delivery_company_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.driverSeria = message.text

        # удалить старую клавиатуру
        types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(chat_id, config.warehouse_number_message)
        bot.register_next_step_handler(msg, process_warehouse_step)
    except Exception:
        error_message(message)


def process_warehouse_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.driverDate = message.text

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        nalozhka_btn = types.KeyboardButton('Наложенный платеж')
        prepaid_btn = types.KeyboardButton('Предоплата на карту')
        markup.add(nalozhka_btn, prepaid_btn)

        msg = bot.send_message(chat_id, config.payment_method_message, reply_markup=markup)
        bot.register_next_step_handler(msg, process_payment_step)
    except Exception:
        error_message(message)


def process_payment_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.car = message.text

        # удалить старую клавиатуру
        types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(chat_id, config.comment_order_message)
        bot.register_next_step_handler(msg, process_comment_step)
    except Exception:
        error_message(message)


def process_comment_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.carModel = message.text

        bot.send_message(chat_id, config.thanks_message)
        bot.send_message(chat_id, getRegData(user, 'Ваша заявка', message.from_user.first_name), parse_mode="Markdown")
        # отправить дубль в группу
        # bot.send_message(config.forward_chat_id, getRegData(user, 'Заявка от бота', bot.get_me().username), parse_mode="Markdown")
    except Exception:
        error_message(message)


# формирует вид заявки регистрации
# нельзя делать перенос строки Template
# в send_message должно стоять parse_mode="Markdown"
def getRegData(user, title, name):
    t = Template(
        '$title *$name* \n Размер: *$userCity* \n ФИО: *$fullname* \n Телефон: *$phone* \n Доставка: *$driverSeria* \n Город, область: *$driverNumber* \n Отделение: *$driverDate* \n Оплата: *$car* \n Комментарий: *$carModel*')

    return t.substitute({
        'title': title,
        'name': name,
        'userCity': user.city,
        'fullname': user.fullname,
        'phone': user.phone,
        'driverSeria': user.driverSeria,
        'driverNumber': user.driverNumber,
        'driverDate': user.driverDate,
        'car': user.car,
        'carModel': user.carModel
    })


# если прислали произвольное фото
@bot.message_handler(content_types=["photo"])
def send_help_text(message):
    bot.send_message(message.chat.id, config.error_image_message)


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
# bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
# bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True)
