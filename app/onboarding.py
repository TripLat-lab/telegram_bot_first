import asyncio
from datetime import datetime
from typing import Dict, List
import html

from aiogram import Bot, types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.storage.models import History, async_session


router = Router()

# ================== НАСТРОЙКИ ==================
ADMIN_ID = 950860793  # ❗ ЗАМЕНИ НА СВОЙ ID

POLL_DELAYS = {
    "week1": 10,     # неделя
    "month1": 20,   # месяц
    "month3": 30    # 3 месяца
    # для тестов можно поставить 10, 20, 30
}

# ================== ТЕКСТЫ ИЗ ТЗ ==================
INTRO_TEXTS = {
    "week1": (
        "Привет! 😃\n\n"
        "Чтобы тебе было комфортно и успешно в нашей команде, просим уделить пару минут "
        "и ответить на несколько вопросов о твоей первой неделе. Твоё мнение очень важно! 🚀\n\n"
        "Спасибо за участие в пульс-опросе! Твое мнение важно для нас.\n\n"
        "Мы понимаем, что вопросы могут возникать, и адаптация — процесс непростой.\n"
        "Учись и расти! Мы верим в твой потенциал!\n\n"
        "Не бойся задавать вопросы — мы рядом и готовы помочь!"
    ),

    "month1": (
        "Привет! 👋\n\n"
        "Вот и пролетел твой первый месяц работы в нашей компании! 🗓️\n\n"
        "Самое время подвести итоги, вспомнить договорённости и подготовиться "
        "к разговору с руководителем.\n\n"
        "Ответь, пожалуйста, на несколько вопросов ниже."
    ),

    "month3": (
        "Привет! 👋\n\n"
        "Пролетели 3 месяца с твоего трудоустройства! 🎉\n\n"
        "Поздравляем с успешным прохождением испытательного срока.\n\n"
        "Оцени свои достижения и вспомни договорённости — это важно."
    )
}

# ================== FSM ==================
class OnboardingStates(StatesGroup):
    week1 = State()
    month1 = State()
    month3 = State()

# ================== ВОПРОСЫ ==================
week1_questions = [
    "1️⃣ Как ты оцениваешь свой первый опыт работы в компании (1-5)?",
    "2️⃣ Насколько тебе понятны твои обязанности и задачи (1-5)?",
    "3️⃣ Насколько ты оцениваешь поддержку со стороны коллег и руководства (1-5)?"
]

month1_questions = [
    "1️⃣ Насколько ты чувствуешь себя частью команды (1-5)?",
    "2️⃣ Насколько тебе интересно выполнять свою работу (1-5)?",
    "3️⃣ Насколько ты понимаешь, как твоя работа влияет на общие цели компании (1-5)?",
    "4️⃣ Какие цели ты ставишь перед собой на следующий месяц?",
    "5️⃣ Какие ресурсы или помощь тебе необходимы?"
]

month3_questions = [
    "1️⃣ Оцени свои достижения за 3 месяца",
    "2️⃣ Какие вопросы хочешь обсудить с руководителем?"
]

# ================== ХРАНЕНИЕ ОТВЕТОВ ==================
class UserAnswers:
    def __init__(self):
        self.answers: Dict[int, Dict[str, List[str]]] = {}

    def add_answer(self, user_id: int, poll_type: str, question: str, answer: str):
        self.answers.setdefault(user_id, {}).setdefault(poll_type, []).append(
            f"❓ {question}\n💬 {answer}"
        )

    def get_answers(self, user_id: int, poll_type: str) -> List[str]:
        return self.answers.get(user_id, {}).get(poll_type, [])

    def clear(self, user_id: int, poll_type: str):
        if user_id in self.answers and poll_type in self.answers[user_id]:
            del self.answers[user_id][poll_type]

user_answers = UserAnswers()

# ================== БД ==================
async def send_question(bot: Bot, user_id: int, question: str, period: str):
    await bot.send_message(user_id, question)

    async with async_session() as session:
        history = History(
            user_id=user_id,
            chat_user=question,
            chat_data=datetime.utcnow(),
            chat_admin=None
        )
        setattr(history, f"data_{7 if period=='week1' else 30 if period=='month1' else 90}", datetime.utcnow())
        session.add(history)
        await session.commit()

async def save_answer(user_id: int, answer: str):
    async with async_session() as session:
        result = await session.execute(
            History.__table__.select()
            .where(History.user_id == user_id, History.chat_admin.is_(None))
            .order_by(History.id.desc())
            .limit(1)
        )
        record = result.first()
        if record:
            await session.execute(
                History.__table__.update()
                .where(History.id == record[0])
                .values(chat_admin=answer, chat_data=datetime.utcnow())
            )
            await session.commit()

# ================== ОТПРАВКА АДМИНУ ==================
async def send_to_admin(bot: Bot, user_id: int, username: str, full_name: str,
                        poll_type: str, answers: List[str]):
    title = {
        "week1": "📅 ОПРОС ПЕРВОЙ НЕДЕЛИ",
        "month1": "📅 ОПРОС ПЕРВОГО МЕСЯЦА",
        "month3": "📅 ОПРОС 3 МЕСЯЦЕВ"
    }[poll_type]

    text = (
        f"<b>{title}</b>\n\n"
        f"👤 {html.escape(full_name)}\n"
        f"🆔 {user_id}\n"
        f"@{username or '—'}\n\n"
    )

    for a in answers:
        text += a + "\n\n"

    await bot.send_message(ADMIN_ID, text, parse_mode="HTML")

# ================== ЗАПУСК ПО ТАЙМЕРУ ==================
async def start_poll_with_delay(user_id: int, bot: Bot, state: FSMContext, poll_type: str):
    await asyncio.sleep(POLL_DELAYS[poll_type])

    await bot.send_message(user_id, INTRO_TEXTS[poll_type])
    await asyncio.sleep(2)

    await start_poll(user_id, bot, state, poll_type)

# ================== ЗАПУСК ОПРОСА ==================
async def start_poll(user_id: int, bot: Bot, state: FSMContext, poll_type: str):
    user_answers.clear(user_id, poll_type)

    questions = {
        "week1": week1_questions,
        "month1": month1_questions,
        "month3": month3_questions
    }[poll_type]

    await state.set_state(getattr(OnboardingStates, poll_type))
    await state.update_data(
        questions=questions,
        current_question_index=1,
        period=poll_type
    )

    await send_question(bot, user_id, questions[0], poll_type)

# ================== ХЭНДЛЕР ОТВЕТОВ ==================
@router.message(F.text & ~F.text.startswith("/"))
async def handle_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data:
        return

    questions = data["questions"]
    idx = data["current_question_index"] - 1
    period = data["period"]

    await save_answer(message.from_user.id, message.text)

    user_answers.add_answer(
        message.from_user.id,
        period,
        questions[idx],
        message.text
    )

    if idx + 1 < len(questions):
        await send_question(message.bot, message.from_user.id, questions[idx + 1], period)
        await state.update_data(current_question_index=idx + 2)
    else:
        await send_to_admin(
            message.bot,
            message.from_user.id,
            message.from_user.username,
            message.from_user.full_name,
            period,
            user_answers.get_answers(message.from_user.id, period)
        )
        user_answers.clear(message.from_user.id, period)
        await state.clear()
        await message.answer("✅ Спасибо! Опрос завершён.")

