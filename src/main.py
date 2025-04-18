import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)

from config import TOKEN, admins
from keyboards import Catalog, Start, back_button
import utils

dp = Dispatcher()


class AdminForm(StatesGroup):
    admin = State()
    new_message = State()


class CatalogForm(StatesGroup):
    category = State()


def generate_category_markup(data, parent_callback):
    kb = [
        [InlineKeyboardButton(text=sub, callback_data=f"{parent_callback}x{i}")]
        for i, sub in enumerate(data)
    ]
    kb.append([back_button])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def generate_simple_markup():
    return InlineKeyboardMarkup(inline_keyboard=[[back_button]])


async def send_admin_panel(message: Message, state: FSMContext):
    await message.answer(
        "🔧 **Админ-панель**\nВыберите необходимый раздел:", reply_markup=Catalog.markup
    )
    await state.set_state(AdminForm.admin)


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    await message.answer(
        f"👋 **Привет, {message.from_user.full_name}!**\nДобро пожаловать в наш каталог мебели и товаров для дома. Выберите интересующий вас раздел ниже ⬇️",
        reply_markup=Start.markup,
    )
    await state.clear()


@dp.message(Command("admin"))
async def admin_command_handler(message: Message, state: FSMContext):
    if message.chat.id in admins:
        await send_admin_panel(message, state)


@dp.callback_query(AdminForm.admin)
async def admin_callback_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data == "back":
        await callback.message.edit_text(
            "🔙 **Главное меню**\nВыберите нужный раздел:", reply_markup=Start.markup
        )
    else:
        data = utils.get_categories()
        if not "x" in callback.data:
            category = list(data.keys())[int(callback.data)]
            category_value = data[category]

            if category_value:
                markup = generate_category_markup(category_value, callback.data)
                await callback.message.edit_text(
                    "📂 **Выберите подкатегорию:**", reply_markup=markup
                )
            else:
                await state.update_data(category=callback.data)
                await callback.message.edit_text(
                    "✍️ **Введите сообщение для этой категории** или нажмите **'Назад'**",
                    reply_markup=generate_simple_markup(),
                )
                await state.set_state(AdminForm.new_message)
        else:
            await state.update_data(category=callback.data)
            await callback.message.edit_text(
                "✍️ **Введите сообщение для этой категории** или нажмите **'Назад'**",
                reply_markup=generate_simple_markup(),
            )
            await state.set_state(AdminForm.new_message)


@dp.callback_query(AdminForm.new_message)
async def cancel_new_message(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await send_admin_panel(callback.message, state)


@dp.message(AdminForm.new_message)
async def new_message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    messages = utils.get_messages()

    category = data["category"]
    messages.setdefault(category, []).append(
        {"chat_id": message.chat.id, "message_id": message.message_id}
    )
    utils.save_messages(messages)

    await message.answer(
        "✅ **Сообщение добавлено!**\nВы можете ввести ещё одно сообщение или нажать **'Назад'**",
        reply_markup=generate_simple_markup(),
    )


@dp.callback_query()
async def general_callback_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data == "catalog":
        await callback.message.edit_text(
            "🛍 **Выберите категорию товаров:**", reply_markup=Catalog.markup
        )
    elif callback.data in ["about", "contacts"]:
        text = (
            "ℹ️ **О нас**\nМы предлагаем широкий ассортимент мебели и товаров для дома высокого качества!"
            if callback.data == "about"
            else "📞 **Контакты**\nСвяжитесь с нами по телефону: +79286572230"
        )
        await callback.message.edit_text(text, reply_markup=generate_simple_markup())
    elif callback.data == "back":
        await callback.message.edit_text(
            "🔙 **Главное меню**\nВыберите нужный раздел:", reply_markup=Start.markup
        )
    else:
        data = utils.get_categories()
        if not "x" in callback.data:
            category = list(data.keys())[int(callback.data)]
            category_value = data[category]

            if category_value:
                markup = generate_category_markup(category_value, callback.data)
                await callback.message.edit_text(
                    "📂 **Выберите подкатегорию:**", reply_markup=markup
                )
            else:
                await state.update_data(category=callback.data)
                messages = utils.get_messages().get(callback.data, [])
                await callback.message.delete()

                print(callback.data)

                if messages:
                    print(callback.data)
                    for item in messages:
                        try:
                            await callback.bot.copy_message(
                                callback.message.chat.id,
                                item["chat_id"],
                                item["message_id"]
                            )
                            await asyncio.sleep(0.5)
                        except Exception as e:
                            print(item["chat_id"], item["message_id"])

                            print(e)
                else:
                    await callback.message.answer(
                        "ℹ️ **В этой категории пока ничего нет.**"
                    )

                await callback.message.answer(
                    "🛍 **Выберите категорию товаров:**", reply_markup=Catalog.markup
                )
        else:
            await state.update_data(category=callback.data)
            messages = utils.get_messages().get(callback.data, [])
            await callback.message.delete()

            if messages:
                print(callback.data)
                for item in messages:
                    try:
                        await callback.bot.copy_message(
                            callback.message.chat.id,
                            item["chat_id"],
                            item["message_id"]
                        )
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        print(item["chat_id"], item["message_id"])

                        print(e)
            else:
                await callback.message.answer("ℹ️ **В этой категории пока ничего нет.**")

            await callback.message.answer(
                "🛍 **Выберите категорию товаров:**", reply_markup=Catalog.markup
            )


@dp.message(Command("delete"))
async def delete_handler(message: Message, state: FSMContext):
    if message.chat.id in admins and message.reply_to_message:
        messages = utils.get_messages()
        message_id = message.reply_to_message.message_id

        for category, items in messages.items():
            messages[category] = [
                item for item in items if item["message_id"] != message_id
            ]

        utils.save_messages(messages)
        await message.answer("🗑 **Сообщение удалено!**")


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
