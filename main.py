from telebot.types import ReplyKeyboardMarkup
from telebot.types import Message
from GPT import *
import logging
from config import *
bot = TeleBot(TOKEN)
MAX_LETTERS = 400

users_history = {}

continue_content = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="errors.txt",
    filemode="w",
)
def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("errors.txt", "rb") as f:
        bot.send_document(message.chat.id, f)

@bot.message_handler(commands=['start'])
def start(message: Message):
    logging.info("Получена команда /start")
    bot.send_message(message.chat.id,
                     text=f'Привет, {message.from_user.first_name}! Я - бот для решения твоих задачек. Для списка команд бота нажмите "меню" левее поля для ввода сообщения',
                     reply_markup=create_keyboard(["/solve_task", '/help']))


@bot.message_handler(commands=['help'])
def support(message):
    logging.info("Получена команда /help")
    bot.send_message(message.from_user.id,
                     text="Чтобы приступить к решению задачи: нажми /solve_task, а затем напиши условие задачи",
                     reply_markup=create_keyboard(["/solve_task"]))


@bot.message_handler(commands=['solve_task'])
def solve_task(message):
    logging.info("Получена команда /solve_task")
    bot.send_message(message.chat.id, "Напиши условие новой задачи:")
    bot.register_next_step_handler(message, get_prompt)


def continue_filter(message):
    button_text = 'Продолжить решение'
    return message.text == button_text

@bot.message_handler(func=continue_filter)
def get_prompt(message):
    if message.content_type != "text":
        bot.send_message(message.from_user.id, "Необходимо отправить именно текстовое сообщение")
        bot.register_next_step_handler(message, get_prompt)
        return

    if len(message.text) > MAX_LETTERS:
        bot.send_message(message.from_user.id, "Запрос превышает количество символов\nИсправь запрос")
        bot.register_next_step_handler(message, get_prompt)
        return
    if message.text == 'Продолжить решение':
            bot.send_message(message.from_user.id, continue_my_work(message, users_history[message.from_user.id]['assistant_content']))
    if message.from_user.id not in users_history or users_history[message.from_user.id] == {}:
        users_history[message.from_user.id] = {
            'system_content': "Ты - дружелюбный помощник для решения задач по математике. Давай подробный ответ с решением на русском языке",
            'user_content': message.text,
            'assistant_content': ""
        }
        logging.info(f"Новый пользователь {message.from_user.first_name}! ID: {message.from_user.id}")
        users_history[message.from_user.id]['assistant_content'] += str(do_my_work(message,
                                                                                       system_content="Ты - дружелюбный помощник для решения задач по математике. Давай подробный ответ с решением на русском языке"))
        global continue_content
        continue_content = "Ты - дружелюбный помощник для решения задач по математике. Продолжи незаконченное решение:" + users_history[message.from_user.id]['assistant_content']
        bot.send_message(message.from_user.id, text=users_history[message.from_user.id]['assistant_content'],
                         reply_markup=create_keyboard(["Продолжить решение", "Завершить решение"]))


def end_filter(message):
    return message.text == 'Завершить решение'


@bot.message_handler(content_types=['text'], func=end_filter)
def end_task(message):
    bot.send_message(message.from_user.id, "Текущие решение завершено")
    users_history[message.from_user.id] = {}
    solve_task(message)


bot.polling()
