import os

from dotenv import load_dotenv

load_dotenv("bot.env")

TOKEN = os.getenv("TOKEN")


CATEGORIES_PATH = "../categories.json"
MESSAGES_PATH = "../messages.json"

admins = [
    700178752,
    1245902436,
    6077616211
]
