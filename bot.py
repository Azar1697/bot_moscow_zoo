import asyncio


import os
from aiofiles import os
from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.utils.markdown import hbold
from aiogram.types import FSInputFile   # ДОБАВЬ в импорты
from config import BOT_TOKEN
from quiz_data import questions, results


class Quiz(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    q6 = State()
    q7 = State()


def make_kb(idx: int):
    builder = ReplyKeyboardBuilder()
    for opt in questions[idx]["options"]:
        builder.button(text=opt["text"])
    builder.adjust(1)                         # по одной кнопке в строке
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


async def ask(idx: int, message: types.Message, state: FSMContext):
    await message.answer(questions[idx]["text"], reply_markup=make_kb(idx))
    await state.set_state(getattr(Quiz, f"q{idx+1}"))


def add_score(score: dict, text: str, idx: int):
    for opt in questions[idx]["options"]:
        if opt["text"] == text:
            score[opt["animal"]] = score.get(opt["animal"], 0) + 1
            break
    return score


async def show_result(message: types.Message, score: dict):
    animal = max(score, key=score.get)
    info = results[animal]

    text = (
        f"Ваше тотемное животное — {hbold(info['name'])}! 🐾\n\n"
        f"{info['description']}"
    )

    try:
        await message.answer_photo(
            photo=FSInputFile(info["image"]),   # если файла нет → FileNotFoundError
            caption=text,
            parse_mode="HTML"
        )
    except FileNotFoundError:
        await message.answer(text, parse_mode="HTML")

    # INLINE-кнопка «Пройти ещё раз»
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text="🔄 Пройти ещё раз", callback_data="restart")
    await message.answer("Хотите попробовать снова?", reply_markup=kb_builder.as_markup())



bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)


@router.message(CommandStart(), StateFilter(None))
async def cmd_start(msg: types.Message, state: FSMContext):
    await state.clear()
    await state.update_data(score={})
    await msg.answer(
        "Привет! Это викторина «Какое у вас тотемное животное?» от Московского зоопарка."
    )
    await ask(0, msg, state)


@router.message(StateFilter(Quiz.q1))
async def q1(msg: types.Message, state: FSMContext):
    d = await state.get_data()
    await state.update_data(score=add_score(d["score"], msg.text, 0))
    await ask(1, msg, state)


@router.message(StateFilter(Quiz.q2))
async def q2(msg: types.Message, state: FSMContext):
    d = await state.get_data()
    await state.update_data(score=add_score(d["score"], msg.text, 1))
    await ask(2, msg, state)


@router.message(StateFilter(Quiz.q3))
async def q3(msg: types.Message, state: FSMContext):
    d = await state.get_data()
    await state.update_data(score=add_score(d["score"], msg.text, 2))
    await ask(3, msg, state)


@router.message(StateFilter(Quiz.q4))
async def q4(msg: types.Message, state: FSMContext):
    d = await state.get_data()
    await state.update_data(score=add_score(d["score"], msg.text, 3))
    await ask(4, msg, state)


@router.message(StateFilter(Quiz.q5))
async def q5(msg: types.Message, state: FSMContext):
    d = await state.get_data()
    await state.update_data(score=add_score(d["score"], msg.text, 4))
    await ask(5, msg, state)


@router.message(StateFilter(Quiz.q6))
async def q6(msg: types.Message, state: FSMContext):
    d = await state.get_data()
    await state.update_data(score=add_score(d["score"], msg.text, 5))
    await ask(6, msg, state)


@router.message(StateFilter(Quiz.q7))
async def q7(msg: types.Message, state: FSMContext):
    d = await state.get_data()
    await state.clear()
    await show_result(msg, d["score"])


@dp.callback_query(F.data == "restart")
async def restart(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.delete_reply_markup()
    await state.clear()
    await state.update_data(score={})
    await ask(0, cb.message, state)
    await cb.answer()


async def main():
    print("Bot running (aiogram 3)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
