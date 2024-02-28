from telebot import *
import requests
import logging

token = TOKEN
bot = telebot.TeleBot(token)

def do_my_work(message, system_content):
    resp = requests.post(
        'http://localhost:1234/v1/chat/completions',

        headers={"Content-Type": "application/json"},

        json={
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": str(message.text)},
            ],
            "temperature": 1.2,
            "max_tokens": 400,
        }
    )
    if resp.status_code == 200:
        return(resp.json()['choices'][0]['message']['content'])
    else:
        print(resp.json)
        logging.error(f"Ошибка у пользователя {message.from_user.first_name}.")
        bot.send_message(message.from_user.id, 'Что-то сломалось:-( . Разраб уже бежит чинить!')
        return None

def continue_my_work(message, content):
    resp = requests.post(
        'http://localhost:1234/v1/chat/completions',

        headers={"Content-Type": "application/json"},

        json={
            "messages": [
                {'role': 'system', 'content': 'Ты - дружелюбный помощник для решения задач по математике. Давай подробный ответ с решением на русском языке'},
                {"role": "user", "content": f'Продолжи объяснение задачи: {content}'},
            ],
            "temperature": 1.2,
            "max_tokens": 400,
        }
    )
    if resp.status_code == 200:
        return(resp.json()['choices'][0]['message']['content'])
    else:
        print(resp.json)
        logging.error(f"Ошибка у пользователя {message.from_user.first_name}.")
        bot.send_message(message.from_user.id, 'Что-то сломалось:-( . Разраб уже бежит чинить!')
        return None

print()