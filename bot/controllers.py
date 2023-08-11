import os
import sys
import psycopg2

from aiogram import types
from PIL import Image, ImageFont, ImageDraw

def get_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Моя карта", "Топ игроков"]
    keyboard.add(*buttons)
    buttons = ["Техническая поддержка"]
    keyboard.add(*buttons) #мб добавить просмотр карт других игроков?
                            #хотелось бы расширить меню
    return keyboard

def get_card_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Изменить изображение профиля", "Изменить никнейм"]
    keyboard.add(*buttons)
    buttons = ["Главное меню"]
    keyboard.add(*buttons)

    return keyboard

def goto_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Главное меню"]
    keyboard.add(*buttons)

    return keyboard

def card_process(nickname, league, don, mafia, sheriff, citizen, won, lost, total, mentor):
    try:
        card = Image.open(f"/~/BonchMafia/bot/pictures/frames/{league}_frame.png") #todo
        #font = ImageFont.truetype("Helvetica", 15)

        #draw = ImageDraw.Draw(card) todo

        #draw.text() todo: make a proper text positioning and frames
        card.save(f"/~/BonchMafia/bot/pictures/cards/{nickname}.png")
    except Exception as e:
        print(f'Found an exception at controllers.card_process: {e}')
    
    return

def get_league(won, total):
    if total < 10:
        league = "calibration"
        winrate = 0
    elif 10 <= total <= 48:
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
    
    return league

def check_admin(userid, adminids):
    if userid in adminids:
        return True
    else:
        return False
    
def get_admin_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
            types.InlineKeyboardButton(text='Сделать оповещение', callback_data='admin_notify'),
            #types.InlineKeyboardButton(text='Забанить', callback_data='admin_ban'),
            #types.InlineKeyboardButton(text='Разбанить', callback_data='admin_pardon',),
            types.InlineKeyboardButton(text='Назначить наставника', callback_data='admin_mentor'),
            types.InlineKeyboardButton(text='Внести протокол игры', callback_data='admin_game')
        ]
    keyboard.add(*buttons)
    return keyboard