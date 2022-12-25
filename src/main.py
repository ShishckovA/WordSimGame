import string

from aiogram.contrib.fsm_storage.memory import MemoryStorage
import random
from aiogram.types import BotCommand

from aiogram.dispatcher import FSMContext
from aiogram.utils import markdown
from scipy import spatial
import asyncio
from aiogram import Bot, Dispatcher, types

from config import BotStates, HINTS_INDEXES, TOKEN
from utils import EMBEDDINGS, WORDS


def build_counter(word):
    word_emb = EMBEDDINGS[word]
    words_new = sorted(WORDS, key=lambda x: spatial.distance.cosine(word_emb, EMBEDDINGS[x]))
    word_to_dist = {v: i for i, v in enumerate(words_new)}
    return word_to_dist, words_new


def new_game():
    word = random.choice(WORDS)
    word_to_dist, dist_to_word = build_counter(word)

    return word, word_to_dist, dist_to_word


async def cmd_start(message: types.Message, state: FSMContext):
    cur_state = await state.get_state()
    if cur_state == BotStates.game_started.state:
        await finish_game(message, state)
    await state.finish()
    await BotStates.game_started.set()
    word, word_to_dist, dist_to_word = new_game()
    data = {
        "word": word,
        "word_to_dist": word_to_dist,
        "dist_to_word": dist_to_word,
        "hints_used": 0,
        "guesses": []
    }
    await state.update_data(data)
    await message.answer("Игра начата!")


async def get_state(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(str(data)[:500])


def normalize(guess: str):
    return guess.replace("ё", "е").lower()


async def handle_guess(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target_word = data["word"]
    word_to_dist = data["word_to_dist"]
    guesses = data["guesses"]
    guess = normalize(message.text)
    answer = f"Твоё слово: {markdown.bold(guess)}"
    if guess == target_word:
        answer += markdown.escape_md("\nПраивльно!")
        await message.answer(answer, parse_mode="MarkdownV2")
        await finish_game(message, state)
        return
    if guess in word_to_dist:
        answer += f"\nПохожесть: *{word_to_dist[guess]}*"
        guesses.append(guess)
        data = {
            "guesses": guesses
        }
        await state.update_data(data)
        await message.answer(answer, parse_mode="MarkdownV2")
    else:
        answer += markdown.escape_md("\nЯ не знаю твоего слова!")
        await message.answer(answer, parse_mode="MarkdownV2")


async def top(message: types.Message, state: FSMContext):
    data = await state.get_data()
    word_to_dist = data["word_to_dist"]
    guesses = data["guesses"]
    words_dists = list(set((word_to_dist[word], word) for word in guesses))
    words_dists.sort(key=lambda x: x[0])
    answer = markdown.escape_md("Ваши лучшие поп-ытки:")
    for dist, word in words_dists[:10]:
        answer += f"\n{dist}: {markdown.bold(word)}"
    await message.answer(answer, parse_mode="MarkdownV2")


async def finish_game(message, state):
    data = await state.get_data()
    answer = markdown.escape_md("Игра окончена!")
    answer += f"\nЗагаданное слово: {markdown.bold(data['word'])}"
    answer += f"\nНеправильных попыток: {markdown.bold(len(data['guesses']))}"
    answer += f"\nПодсказок использовано: {markdown.bold(data['hints_used'])}"
    await message.answer(answer,
                         parse_mode="Markdownv2")
    await state.finish()


async def hint(message, state):
    data = await state.get_data()
    dist_to_word = data["dist_to_word"]
    hints_used = data["hints_used"] + 1
    answer = "Подсказки:"
    for ind in HINTS_INDEXES[:hints_used]:
        answer += f"\n{ind}: {markdown.bold(dist_to_word[ind])}"
    await state.update_data({
        "hints_used": hints_used
    })
    await message.answer(answer, parse_mode="MarkdownV2")


async def handle_messaage(message, state):
    await message.answer("Игра пока не начата =(")


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать игру"),
        BotCommand(command="/finish", description="Оконить игру"),
        BotCommand(command="/hint", description="Подсказка!"),
    ]
    await bot.set_my_commands(commands)


async def main():
    bot = Bot(token=TOKEN)
    await set_commands(bot)

    dp = Dispatcher(bot, storage=MemoryStorage())

    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(get_state, commands="state", state="*")
    dp.register_message_handler(finish_game, commands="finish", state=BotStates.game_started)
    dp.register_message_handler(top, commands="top", state=BotStates.game_started)
    dp.register_message_handler(hint, commands="hint", state=BotStates.game_started)
    dp.register_message_handler(handle_guess, state=BotStates.game_started)
    dp.register_message_handler(handle_messaage, state="*")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
