import os
import sys
import psycopg2

from aiogram import types
from PIL import Image, ImageFont, ImageDraw, ImageFilter, ImageOps
from bot.dispatcher import bot

def get_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Моя карта", "Другой игрок"]
    keyboard.add(*buttons)
    buttons = ["Техническая поддержка"]
    keyboard.add(*buttons) 
                            #хотелось бы расширить меню
    return keyboard

def get_card_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Изменить изображение", "Изменить никнейм"]
    keyboard.add(*buttons)
    buttons = ["Главное меню"]
    keyboard.add(*buttons)

    return keyboard

def goto_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Главное меню"]
    keyboard.add(*buttons)

    return keyboard

def profile_circular_process(nickname):
    try:
        mask = Image.open('/~/BonchMafia/bot/pictures/profile/avatar_mask.png').convert('L')
        profile_image = Image.open(f'/~/BonchMafia/bot/pictures/profile/{nickname}_temp.png')

        output = ImageOps.fit(profile_image, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)

        output.save(f'/~/BonchMafia/bot/pictures/profile/{nickname}.png')

        if os.path.exists(f'/~/BonchMafia/bot/pictures/profile/{nickname}_temp.png'):
            os.remove(f'/~/BonchMafia/bot/pictures/profile/{nickname}_temp.png')
        else:
            print(f"File f'/~/BonchMafia/bot/pictures/profile/{nickname}_temp.png' doesn't exist")

    except Exception as e:
        print(f'Found an exception at profile_circular_process: {e}')

def get_textbox(draw, msg, font):
    _, _, w, h = draw.textbbox((0, 0), msg, font=font)
    return w, h

def card_process(nickname, league, don, don_total, mafia, mafia_total, sheriff, sheriff_total, citizen, citizen_total, won, lost, total, mentor):
    try:
        background = Image.open(f"/~/BonchMafia/bot/pictures/{league}/background.png")
        backplate = Image.open(f"/~/BonchMafia/bot/pictures/{league}/backplate.png")
        profile_picture = Image.open(f"/~/BonchMafia/bot/pictures/profile/{nickname}.png")

        logo = Image.open(f"/~/BonchMafia/bot/pictures/{league}/logo.png")
        
        don_icon = Image.open(f"/~/BonchMafia/bot/pictures/{league}/don.png")
        citizen_icon = Image.open(f"/~/BonchMafia/bot/pictures/{league}/citizen.png")
        mafia_icon = Image.open(f"/~/BonchMafia/bot/pictures/{league}/mafia.png")
        sheriff_icon = Image.open(f"/~/BonchMafia/bot/pictures/{league}/sheriff.png")
        total_icon = Image.open(f"/~/BonchMafia/bot/pictures/{league}/total.png")

        icon_size = (55, 55)
        don_icon = don_icon.resize(icon_size)
        citizen_icon = citizen_icon.resize(icon_size)
        mafia_icon = mafia_icon.resize(icon_size)
        sheriff_icon = sheriff_icon.resize(icon_size)
        total_icon = total_icon.resize(icon_size)
        
        stats_font = ImageFont.truetype("/~/BonchMafia/bot/pictures/fonts/VelaSans-Bold.otf", 24)
        your_league_font = ImageFont.truetype("/~/BonchMafia/bot/pictures/fonts/VelaSans-Regular.otf", 36)
        league_font = ImageFont.truetype("/~/BonchMafia/bot/pictures/fonts/VelaSans-ExtraBold.otf", 36)
        nickname_font = ImageFont.truetype("/~/BonchMafia/bot/pictures/fonts/VelaSans-SemiBold.otf", 48)
        your_mentor_font = ImageFont.truetype("/~/BonchMafia/bot/pictures/fonts/VelaSans-Light.otf", 20)
        mentor_font = ImageFont.truetype("/~/BonchMafia/bot/pictures/fonts/VelaSans-Light.otf", 20)
        roles_font = ImageFont.truetype("/~/BonchMafia/bot/pictures/fonts/VelaSans-Light.otf", 14)

        card = background.copy()

        backplate_size = (360, 360)
        backplate = backplate.resize(backplate_size)

        card.paste(backplate, (180, 182), backplate)
        card.paste(profile_picture, (185, 187), profile_picture)
        card.paste(logo, (499, 1032), logo)

        card.paste(total_icon, (333, 913), total_icon)

        card.paste(sheriff_icon, (483, 699), sheriff_icon)
        card.paste(citizen_icon, (182, 699), citizen_icon)

        card.paste(don_icon, (483, 795), don_icon)
        card.paste(mafia_icon, (182, 795), mafia_icon)
        
        draw = ImageDraw.Draw(im=card)

        if league == "calibration":
            league_text = "ОПРЕДЕЛЯЕТСЯ"
            stats_color = "#BB7F41"
            your_league_color = "#BB7F41"
            nickname_color = "#BB7F41"
            mentor_color = "#BB7F41"

        elif league == "bronze":
            stats_color = "#E6BC97"
            your_league_color = "#E6BC97"
            nickname_color = "#E6BC97"
            mentor_color = "#E6BC97"
            league_text = "БРОНЗА"

        elif league == "silver":
            league_text = "СЕРЕБРО"
            stats_color = "#ECEAE4"
            your_league_color = "#ECEAE4"
            nickname_color = "#ECEAE4"
            mentor_color = "#ECEAE4"

        elif league == "gold":
            league_text = "ЗОЛОТО"
            stats_color = "#EEBB6C"
            your_league_color = "#EEBB6C"
            nickname_color = "#EEBB6C"
            mentor_color = "#EEBB6C"

        elif league == "platinum":
            league_text = "ПЛАТИНА"
            stats_color = "#C5C5C5"
            your_league_color = "#C5C5C5"
            nickname_color = "#C5C5C5"
            mentor_color = "#C5C5C5"

        elif league == "ruby":
            league_text = "РУБИН"
            stats_color = "#FF8585"
            your_league_color = "#FF8585"
            nickname_color = "#FF8585"
            mentor_color = "#FF8585"

        elif league == "diamond":
            league_text = "АЛМАЗ"
            stats_color = "#5ED2F8"
            your_league_color = "#5ED2F8"
            nickname_color = "#5ED2F8"
            mentor_color = "#5ED2F8"

        else:
            league_text = "UNKNOWN"
            stats_color = "#f"
            your_league_color = "#f"
            nickname_color = "#f"
            mentor_color = "#f"
            print(f"Found wrong league at card processing: {league}")

        w, h = get_textbox(draw, nickname, nickname_font)
        draw.text(((720-w)/2, 563), nickname, nickname_color, nickname_font)

        draw.text((423, 699), "ШЕРИФ", stats_color, roles_font, align="right")
        draw.text((430, 718), f"{sheriff}/{sheriff_total}", stats_color, stats_font, align="left")
        
        draw.text((247, 699), "МИРНЫЙ", stats_color, roles_font, align="left")
        draw.text((247, 718), f"{citizen}/{citizen_total}", stats_color, stats_font, align="right")

        draw.text((443, 795), "ДОН", stats_color, roles_font, align="right")
        draw.text((430, 814), f"{don}/{don_total}", stats_color, stats_font, align="left")

        draw.text((247, 795), "МАФИЯ", stats_color, roles_font, align="left")
        draw.text((247, 814), f"{mafia}/{mafia_total}", stats_color, stats_font, align="right")

        draw.text((314, 862), "ВСЕГО ПОБЕД", stats_color, roles_font)
        w, h = get_textbox(draw, f"{won}/{total}", stats_font)
        draw.text(((720-w)/2, 879), f"{won}/{total}", stats_color, stats_font, align="center")

        w, h = get_textbox(draw, "ТВОЙ РАНГ:", your_league_font)
        draw.text(((720-w)/2, 62), "ТВОЙ РАНГ:", your_league_color, your_league_font)

        w, h = get_textbox(draw, league_text, league_font)
        draw.text(((720-w)/2, 110), league_text, your_league_color, league_font)

        if mentor!='-':
            w, h = get_textbox(draw, "НАСТАВНИК:", mentor_font)
            draw.text(((728-w)/2, 624), "НАСТАВНИК:", mentor_color, mentor_font)

            w, h = get_textbox(draw, mentor, mentor_font)
            draw.text(((723-w)/2, 647), mentor, mentor_color, mentor_font)

        card.save(f"/~/BonchMafia/bot/pictures/cards/{nickname}.png")
        return 0

    except Exception as e:
        print(f'Found an exception at controllers.card_process: {e}')
        
        return 1
    
    return

def get_league(won, total):
    if total < 10:
        winrate = -1
    elif 10 <= total <= 48:
        winrate = round(won/48)*100
    else:
        winrate = round(won/total)*100

    if winrate == -1:
        league = "calibration"
    elif 0 <= winrate <= 16:
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
    
def get_admin_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
            #types.InlineKeyboardButton(text='Сделать оповещение', callback_data='admin_notify'),
            #types.InlineKeyboardButton(text='Забанить', callback_data='admin_ban'),
            #types.InlineKeyboardButton(text='Разбанить', callback_data='admin_pardon',),
            types.InlineKeyboardButton(text='Назначить наставника', callback_data='admin_mentor'),
            types.InlineKeyboardButton(text='Внести протокол игры', callback_data='admin_game')
        ]
    keyboard.add(*buttons)
    return keyboard

async def get_username(user_id):
    try:
        chat = await bot.get_chat(user_id)
        username = chat.username
        return username
    except Exception as e:
        print("Error while getting username:", e)
        return "404n0tF0uNd"