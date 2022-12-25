from aiogram.dispatcher.filters.state import StatesGroup, State
import os


class BotStates(StatesGroup):
    game_started = State()


HINTS_INDEXES = [1000, 500, 100, 50, 25, 10, 5]

EMBEDDINGS_PATH = "models/navec_hudlit_v1_12B_500K_300d_100q.tar"
WORDS_PATH = "dictionaries/words.txt"
TOKEN = os.getenv("TOKEN")
