import sys
import psycopg2
import random
import aiogram.utils.markdown as fmt
from PIL import Image, ImageFont, ImageDraw

from bot.disaptcher import dp, bot
from aiogram import types
from time import sleep
#from bot.controllers import //todo functions here
from bot import DB, USER, PASSWORD, HOST, ADMIN
from aiogram.utils.exceptions import BotBlocked
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

"""
Подключение к БД
"""

while flag:
    try:
        conn = psycopg2.connect(dbname=DB, user=USER, password=PASSWORD, host=HOST) #указывать в .env
        print('Connection to database is established')
        flag = False
    except Exception as e:
        print("Can't establish connection to database. Error:", e)
        sleep(3)


"""
todo Блок для работы с блокировкой и разблокировкой пользователей
"""


"""
Главное меню
"""

@dp.message_handler(Text(equals="Техническая поддержка"))
async def support(message: types.Message):
    await message.answer(f'По всем вопросам обращайтесь в личные сообщения группы ВК (https://vk.com/bonchmafia).\nИли в наш телеграм канал (*ВСТАВИТЬ ССЫЛКУ ЗДЕСЬ*).')

@dp.message_handler(commands="start")
@dp.message_handler(Text(equals="Начать"))
async def greeter(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    goto_menu = types.KeyboardButton(text="Главное меню")
    keyboard.add(goto_menu)
    await message.answer(greet, reply_markup=keyboard)

"""
Блок с пользовательской картой
"""

@dp.message_handler(Text(equals="Моя карта"))
async def mycard(message: types.Message):
    userid = message.from_user.id
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE userid={userid}")
    userstats = cursor.fetchone()
    cursor.close()
    if len(userstats == 0):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Создать новую карту", callback_data="card_new"))
        await message.answer("Похоже, что вашей карты нет.", reply_markup=keyboard)
    else:
        userid = userstats[1]
        don = userstats[2]
        mafia = userstats[3]
        sheriff = userstats[4]
        citizen = userstats[5]
        won = userstats[6]
        lost = userstats[7]
        total = won+lost
        mentor = userstats[8]
        nickname = userstats[9]

        winrate = round(won/total)*100
        if total < 10:
            league = "calibration"
            winrate = 0
        
        if 10 <= total <= 48:
            winrate = round(won/48)*100
        else:
            winrate = round(won/total)*100

        if winrate <= 16:
            league = "bronze"
        elif 17 <= winrate <= 26:
            league = "silver"
        elif 27 <= winrate <= 37:
            league = "gold"
        elif 38 <= winrate <= 48:
            league = "platinum"
        elif 49 <= winrate <= 59:
            league = "ruby"
        elif winrate >= 60:
            league = "diamond"
        
        card = Image.open(f"frames/{league}_frame.png")
        font = ImageFont.truetype("Helvetica", 15)

        draw = ImageDraw.Draw(card)

        #draw.text() todo: make a proper text positioning and frames
        card.save(f"cards/{nickname}.png")
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Изменить изображение профиля", "Изменить никнейм"]
        keyboard.add(*buttons)
        keyboard.add(["Главное меню"])
        await message.answer_photo(f"cards/{nickname}.png", reply_markup=keyboard)