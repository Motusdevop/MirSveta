from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

from utils import get_categories

back_button = InlineKeyboardButton(text="<-- Назад", callback_data="back")


class Start:
    kb = [
        [InlineKeyboardButton(text="Посмотреть каталог", callback_data="catalog")],
        [
            InlineKeyboardButton(text="Контакты", callback_data="contacts"),
            InlineKeyboardButton(text="О нас", callback_data="about"),
        ],
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=kb)


class Catalog:
    data = get_categories()
    kb = []

    print(data)

    for i in range(len(data.keys())):
        category = list(data.keys())[i]
        kb.append([InlineKeyboardButton(text=category, callback_data=str(i))])

    kb.append([back_button])

    markup = InlineKeyboardMarkup(inline_keyboard=kb)
