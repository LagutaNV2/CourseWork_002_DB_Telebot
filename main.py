import random
import configparser
import random

import telebot
from telebot import types, TeleBot, custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

from Бот_02.query_db import get_users, add_user, add_users_dict, get_words_from_bd, add_word_to_db, \
    delete_word_from_users_dict

print('Start telegram bot...')

state_storage = StateMemoryStorage()

API_URL = 'https://api.telegram.org/bot'
config = configparser.ConfigParser()
config.read('setting.ini')
token = config["TGBot"]["BOT_TOKEN"]

bot = telebot.TeleBot(token)

known_users = []
userStep = {}
buttons = []  # кнопки


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, "Вы вызвали команду help. Но я ещё ничего не умею")


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить это слово из словаря🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = message.chat.id
    print('came cid', cid)

    if get_users(cid) is None:
        # print('not find cid')
        bot.send_message(cid, "Привет 👋 Давай попрактикуемся в иностранном языке. "
                              "Тренировки можешь проходить в удобном для себя темпе."
                              " Сейчас словарь настроен на анлийский язык."
                             " Ты можешь добавлять и удалять слова, формируя свою версию словаря")
        add_user(cid)
        add_users_dict(cid)

    markup = types.ReplyKeyboardMarkup(row_width=2)
    global buttons
    buttons = []
    translate, target_word, others = get_words_from_bd(cid)
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])
    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)

#блок удаления слова из словаря
@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('OK', 'NO')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        greeting = (f"Если в твоем словаре осталось всего 5 слов, удаление будет заблокировано. "
                    f"Удалаем слово: {data['target_word']}?")
        msg = bot.reply_to(message, greeting, reply_markup=markup)
        bot.register_next_step_handler(msg, step_del_2)


def step_del_2(message):
    cid = message.chat.id
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        t_word = data['target_word']

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    next_btn = types.KeyboardButton(Command.NEXT)
    markup.add(next_btn)

    if message.text == 'OK':
        result_del = delete_word_from_users_dict(cid, t_word)
        if result_del == 'Done':
            bot.send_message(message.chat.id, 'выполнено', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'удаление не возможно, осталось мало слов', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'отмена', reply_markup=markup)


#блок добавления слова в словарь
@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    cid = message.chat.id
    userStep[cid] = [cid, 'translate_new', 't_word_new']
    a = types.ReplyKeyboardRemove()
    msg = bot.send_message(cid, "ведите слово и перевод через запятую (пример: Один, One):", reply_markup=a)
    bot.register_next_step_handler(msg, step_add_2)


def step_add_2(message):
    cid = message.chat.id
    words_new = message.text
    if len(words_new) < 3 or ',' not in words_new[1:-1]:
        print('некорректный ввод слов для добавления')
        a = types.ReplyKeyboardRemove()
        msg = bot.send_message(cid, "некорректный ввод! ведите слово и перевод через запятую (пример: Один, One):", reply_markup=a)
        bot.register_next_step_handler(msg, step_add_2)
    else:
        words_new = message.text.split(',')
        userStep[cid][1] = words_new[0].strip()
        userStep[cid][2] = words_new[1].strip()
        print('userStep', userStep[cid])
        print('words', userStep[cid][1], userStep[cid][2])

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('OK', 'NO')
        msg = bot.reply_to(message, 'Добавляем?', reply_markup=markup)
        bot.register_next_step_handler(msg, step_add_3)


def step_add_3(message):
    cid = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    next_btn = types.KeyboardButton(Command.NEXT)
    markup.add(next_btn)

    if message.text == 'OK':
        add_word_to_db(cid, userStep[cid][1], userStep[cid][2])
        bot.send_message(message.chat.id, 'выполнено', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'отмена добавления', reply_markup=markup)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")
    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)

