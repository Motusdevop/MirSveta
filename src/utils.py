import json

from config import CATEGORIES_PATH, MESSAGES_PATH


def get_categories() -> dict:
    with open(CATEGORIES_PATH, "r") as f:
        return json.load(f)


def get_messages() -> dict:
    try:
        with open(MESSAGES_PATH, "r") as f:
            return json.load(f)
    except:
        return dict()


def save_messages(messages: dict) -> None:
    with open(MESSAGES_PATH, "w") as f:
        json.dump(messages, f, indent=4)
