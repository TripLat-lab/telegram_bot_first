from aiogram import Bot, types, F, Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from datetime import datetime
from typing import Dict, List
import html
import asyncio
from app.storage.models import History, async_session

router = Router()

# ID администратора - ЗАМЕНИТЕ ЭТОТ ID НА ВАШ РЕАЛЬНЫЙ ID В TELEGRAM
ADMIN_ID = 744895319  # ⚠️ ЗАМЕНИТЕ НА ВАШ ID!

# ---------------- Класс для хранения ответов ----------------
class UserAnswers:
    """Класс для хранения ответов пользователя"""
    def __init__(self):
        self.answers: Dict[int, Dict[str, List[str]]] = {}
    
    def add_answer(self, user_id: int, poll_type: str, question: str, answer: str):
        """Добавление ответа пользователя"""
        if user_id not in self.answers:
            self.answers[user_id] = {}
        
        if poll_type not in self.answers[user_id]:
            self.answers[user_id][poll_type] = []
        
        # Сохраняем вопрос и ответ
        self.answers[user_id][poll_type].append(f"❓ {question}\n💬 {answer}")
    
    def get_answers(self, user_id: int, poll_type: str) -> List[str]:
        """Получение ответов пользователя"""
        if user_id in self.answers and poll_type in self.answers[user_id]:
            return self.answers[user_id][poll_type]
        return []
    
    def clear_answers(self, user_id: int, poll_type: str):
        """Очистка ответов пользователя"""
        if user_id in self.answers and poll_type in self.answers[user_id]:
            del self.answers[user_id][poll_type]
            
    def get_all_user_answers(self, user_id: int) -> Dict[str, List[str]]:
        """Получение всех ответов пользователя"""
        return self.answers.get(user_id, {})

# Создаем экземпляр для хранения ответов
user_answers = UserAnswers()

# ---------------- FSM ----------------
class OnboardingStates(StatesGroup):
    week1 = State()
    month1 = State()
    month3 = State()


# ---------------- Вопросы ----------------
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
    "5️⃣ Какие ресурсы или помощь тебе необходимы для достижения этих целей?"
]

month3_questions = [
    "1️⃣ Оцени свои достижения за 3 месяца",
    "2️⃣ Какие вопросы или договорённости хочешь обсудить с руководителем?"
]


# ---------------- Функции для работы с БД ----------------
async def send_question(bot: Bot, user_id: int, question: str, period: str) -> int | None:
    """Отправка вопроса пользователю и сохранение в History."""
    try:
        await bot.send_message(chat_id=user_id, text=question)
        
        async with async_session() as session:
            history = History(
                user_id=user_id,
                chat_user=question,
                chat_data=datetime.utcnow(),
                chat_admin=None  # Ожидаем ответ
            )
            
            # Устанавливаем соответствующие даты
            if period == "week1":
                history.data_7 = datetime.utcnow()
            elif period == "month1":
                history.data_30 = datetime.utcnow()
            elif period == "month3":
                history.data_90 = datetime.utcnow()
            
            session.add(history)
            await session.commit()
            return history.id  # Возвращаем ID записи
    except Exception as e:
        print(f"Error in send_question: {e}")
        return None


async def save_answer(user_id: int, answer: str) -> bool:
    """Сохранение ответа пользователя в последнюю запись History."""
    try:
        async with async_session() as session:
            # Ищем последнюю запись для этого пользователя без ответа
            result = await session.execute(
                History.__table__.select()
                .where(History.user_id == user_id, History.chat_admin.is_(None))
                .order_by(History.id.desc())
                .limit(1)
            )
            record = result.first()
            if record:
                history_id = record[0]
                await session.execute(
                    History.__table__.update()
                    .where(History.id == history_id)
                    .values(chat_admin=answer, chat_data=datetime.utcnow())
                )
                await session.commit()
                return True
        return False
    except Exception as e:
        print(f"Error in save_answer: {e}")
        return False


# ---------------- Функция отправки администратору ----------------
async def send_to_admin(bot: Bot, user_id: int, username: str, full_name: str, 
                        poll_type: str, answers: List[str]):
    """Отправка собранных ответов администратору"""
    try:
        # Формируем заголовок сообщения
        poll_titles = {
            "week1": "📅 ОПРОС ПЕРВОЙ НЕДЕЛИ",
            "month1": "📅 ОПРОС ПЕРВОГО МЕСЯЦА", 
            "month3": "📅 ОПРОС ТРЕХ МЕСЯЦЕВ"
        }
        
        poll_title = poll_titles.get(poll_type, poll_type)
        
        # Формируем основное сообщение
        message_text = (
            f"<b>🔄 НОВЫЙ ОТЧЕТ ОПРОСА</b>\n\n"
            f"<b>{poll_title}</b>\n"
            f"👤 <b>Пользователь:</b> {html.escape(full_name)}\n"
            f"🆔 <b>ID:</b> {user_id}\n"
            f"👤 <b>Username:</b> @{username if username else 'отсутствует'}\n"
            f"📅 <b>Дата:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            f"<b>📝 ОТВЕТЫ:</b>\n"
            f"{'='*40}\n"
        )
        
        # Добавляем вопросы и ответы
        for i, answer_text in enumerate(answers, 1):
            message_text += f"\n<b>{i}.</b>\n{answer_text}\n"
            if i < len(answers):
                message_text += "-" * 30 + "\n"
        
        # Отправляем администратору
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=message_text,
            parse_mode='HTML'
        )
        
        print(f"✅ Отчет отправлен администратору для пользователя {user_id}, опрос: {poll_type}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при отправке администратору: {e}")
        return False


# ---------------- Функция сохранения ответа с коллекционированием ----------------
async def save_answer_and_collect(bot: Bot, user_id: int, username: str, full_name: str, 
                                  question: str, answer: str, poll_type: str, 
                                  question_index: int, total_questions: int) -> bool:
    """Сохранение ответа в БД и сбор в коллекцию"""
    try:
        # Сохраняем в базу данных
        saved_to_db = await save_answer(user_id, answer)
        
        if not saved_to_db:
            print(f"⚠️ Не удалось сохранить ответ в БД для пользователя {user_id}")
        
        # Добавляем в коллекцию для отправки администратору
        user_answers.add_answer(user_id, poll_type, question, answer)
        
        # Если это последний вопрос - отправляем администратору
        if question_index >= total_questions - 1:
            answers_list = user_answers.get_answers(user_id, poll_type)
            if answers_list:
                await send_to_admin(
                    bot=bot,
                    user_id=user_id,
                    username=username,
                    full_name=full_name,
                    poll_type=poll_type,
                    answers=answers_list
                )
                # Очищаем собранные ответы
                user_answers.clear_answers(user_id, poll_type)
                print(f"✅ Ответы пользователя {user_id} отправлены администратору")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in save_answer_and_collect: {e}")
        return False


# ---------------- Функции запуска опросов ----------------
async def start_poll(user_id: int, bot: Bot, state: FSMContext, poll_type: str):
    """Запуск опроса определенного типа."""
    # Очищаем предыдущие ответы для этого пользователя и опроса
    user_answers.clear_answers(user_id, poll_type)
    
    if poll_type == "week1":
        await state.set_state(OnboardingStates.week1)
        await state.update_data(
            current_question_index=0,
            questions=week1_questions,
            period="week1",
            next_poll="month1"
        )
        # Отправляем первый вопрос
        await send_question(bot, user_id, week1_questions[0], "week1")
        await state.update_data(current_question_index=1)
        
    elif poll_type == "month1":
        await state.set_state(OnboardingStates.month1)
        await state.update_data(
            current_question_index=0,
            questions=month1_questions,
            period="month1",
            next_poll="month3"
        )
        await send_question(bot, user_id, month1_questions[0], "month1")
        await state.update_data(current_question_index=1)
        
    elif poll_type == "month3":
        await state.set_state(OnboardingStates.month3)
        await state.update_data(
            current_question_index=0,
            questions=month3_questions,
            period="month3",
            next_poll=None
        )
        await send_question(bot, user_id, month3_questions[0], "month3")
        await state.update_data(current_question_index=1)


# ---------------- Команды для запуска опросов ----------------
@router.message(Command("week1"))
async def cmd_week1(message: types.Message, state: FSMContext):
    """Запуск опроса первой недели."""
    current_state = await state.get_state()
    if current_state:
        await message.answer("⚠️ Сначала завершите текущий опрос командой /cancel")
        return
    
    await start_poll(message.from_user.id, message.bot, state, "week1")
    await message.answer("🚀 Начинаем опрос первой недели! Отвечайте на вопросы по порядку.")


@router.message(Command("month1"))
async def cmd_month1(message: types.Message, state: FSMContext):
    """Запуск опроса первого месяца."""
    current_state = await state.get_state()
    if current_state:
        await message.answer("⚠️ Сначала завершите текущий опрос командой /cancel")
        return
    
    await start_poll(message.from_user.id, message.bot, state, "month1")
    await message.answer("📅 Начинаем опрос первого месяца! Отвечайте на вопросы по порядку.")


@router.message(Command("month3"))
async def cmd_month3(message: types.Message, state: FSMContext):
    """Запуск опроса третьего месяца."""
    current_state = await state.get_state()
    if current_state:
        await message.answer("⚠️ Сначала завершите текущий опрос командой /cancel")
        return
    
    await start_poll(message.from_user.id, message.bot, state, "month3")
    await message.answer("🎯 Начинаем опрос третьего месяца! Отвечайте на вопросы по порядку.")


# ---------------- Тестовые команды ----------------
@router.message(Command("test"))
async def cmd_test(message: types.Message, state: FSMContext):
    """Тестовый запуск опроса."""
    current_state = await state.get_state()
    if current_state:
        await message.answer("⚠️ Сначала завершите текущий опрос командой /cancel")
        return
    
    await start_poll(message.from_user.id, message.bot, state, "week1")
    await message.answer("🧪 Тестовый запуск опроса недели. Отвечайте на вопросы.")


@router.message(Command("test_all"))
async def cmd_test_all(message: types.Message):
    """Тестовая команда для проверки отправки всех вопросов."""
    user_id = message.from_user.id
    bot = message.bot
    
    await message.answer("🟢 Тестовая отправка всех опросов...")
    
    try:
        # Отправляем вопросы всех опросов
        for i, (questions, period) in enumerate([
            (week1_questions, "week1"),
            (month1_questions, "month1"),
            (month3_questions, "month3")
        ]):
            await message.answer(f"\n{'='*40}\nОпрос {period}:\n{'='*40}")
            for question in questions:
                await send_question(bot, user_id, question, period)
                await asyncio.sleep(0.3)  # Небольшая задержка
        
        await message.answer("✅ Все тестовые вопросы отправлены и сохранены в БД!")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        print(f"Error in test_all: {e}")


# ---------------- Утилитные команды ----------------
@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Отмена текущего опроса."""
    current_state = await state.get_state()
    if current_state:
        # Получаем данные опроса
        data = await state.get_data()
        period = data.get("period", "")
        
        # Очищаем ответы пользователя для этого опроса
        if period:
            user_answers.clear_answers(message.from_user.id, period)
        
        await state.clear()
        await message.answer("❌ Опрос отменен. Вы можете начать новый.")
    else:
        await message.answer("🤷‍♂️ Нет активного опроса для отмены.")


@router.message(Command("status"))
async def cmd_status(message: types.Message, state: FSMContext):
    """Проверка текущего состояния."""
    current_state = await state.get_state()
    data = await state.get_data()
    
    if current_state:
        state_name = current_state.split(":")[-1] if ":" in current_state else current_state
        await message.answer(
            f"📊 Текущее состояние: {state_name}\n"
            f"Вопросов отвечено: {data.get('current_question_index', 0)}/{len(data.get('questions', []))}\n"
            f"Период: {data.get('period', 'не указан')}\n"
            f"Следующий опрос: {data.get('next_poll', 'нет')}"
        )
    else:
        await message.answer("🟢 Нет активных опросов.")


# ---------------- Админские команды ----------------
@router.message(Command("last_answers"))
async def cmd_last_answers(message: types.Message):
    """Просмотр последних сохраненных ответов (для отладки)"""
    # Только администратор может использовать эту команду
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Эта команда доступна только администратору.")
        return
    
    if not user_answers.answers:
        await message.answer("📭 Нет сохраненных ответов в памяти.")
        return
    
    response = "<b>📊 ПОСЛЕДНИЕ СОХРАНЕННЫЕ ОТВЕТЫ:</b>\n\n"
    
    for user_id, polls in user_answers.answers.items():
        response += f"👤 <b>Пользователь ID:</b> {user_id}\n"
        for poll_type, answers in polls.items():
            response += f"   📅 <b>Опрос:</b> {poll_type}\n"
            response += f"   📝 <b>Ответов:</b> {len(answers)}\n"
            for i, answer in enumerate(answers[:3], 1):  # Показываем только первые 3
                response += f"      {i}. {answer[:50]}...\n"
            if len(answers) > 3:
                response += f"      ... и ещё {len(answers) - 3} ответов\n"
        response += "\n"
    
    # Отправляем сообщение с учетом ограничения длины
    if len(response) > 4000:
        response = response[:3900] + "\n\n... (сообщение слишком длинное, показаны первые ответы)"
    
    await message.answer(response, parse_mode='HTML')


@router.message(Command("send_reports"))
async def cmd_send_reports(message: types.Message):
    """Принудительная отправка всех собранных отчетов администратору"""
    # Только администратор может использовать эту команду
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Эта команда доступна только администратору.")
        return
    
    if not user_answers.answers:
        await message.answer("📭 Нет собранных ответов для отправки.")
        return
    
    sent_count = 0
    for user_id, polls in user_answers.answers.items():
        for poll_type, answers in polls.items():
            # Здесь нужно получить информацию о пользователе
            # В реальном приложении можно получить из базы данных
            # Для теста используем базовую информацию
            username = "unknown"
            full_name = f"User_{user_id}"
            
            await send_to_admin(
                bot=message.bot,
                user_id=user_id,
                username=username,
                full_name=full_name,
                poll_type=poll_type,
                answers=answers
            )
            sent_count += 1
    
    # Очищаем после отправки
    user_answers.answers.clear()
    await message.answer(f"✅ Отправлено {sent_count} отчетов администратору.")


# ---------------- Хэндлер ответов на вопросы (исключает команды) ----------------
@router.message(F.text & ~F.text.startswith('/'))
async def handle_answer(message: types.Message, state: FSMContext):
    """
    Обработка ответов пользователя.
    Исключает команды (текст, начинающийся с /).
    """
    current_state = await state.get_state()
    
    # Проверяем, находится ли пользователь в процессе опроса
    if not current_state:
        # Пользователь не в процессе опроса - игнорируем обычный текст
        return
    
    # Получаем данные текущего опроса
    data = await state.get_data()
    questions = data.get("questions", [])
    current_index = data.get("current_question_index", 0)
    period = data.get("period", "")
    next_poll = data.get("next_poll")
    
    # Определяем, на какой вопрос отвечает пользователь
    # current_index - это индекс следующего вопроса, поэтому предыдущий = current_index - 1
    answered_question_index = current_index - 1
    
    if 0 <= answered_question_index < len(questions):
        current_question = questions[answered_question_index]
    else:
        current_question = "Неизвестный вопрос"
    
    # Получаем информацию о пользователе
    username = message.from_user.username
    full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
    
    # Сохраняем ответ с коллекционированием
    saved = await save_answer_and_collect(
        bot=message.bot,
        user_id=message.from_user.id,
        username=username,
        full_name=full_name,
        question=current_question,
        answer=message.text,
        poll_type=period,
        question_index=answered_question_index,
        total_questions=len(questions)
    )
    
    if not saved:
        await message.answer("⚠️ Не удалось сохранить ответ. Попробуйте еще раз.")
        return
    
    # Проверяем, есть ли еще вопросы
    if current_index < len(questions):
        # Отправляем следующий вопрос
        await send_question(message.bot, message.from_user.id, questions[current_index], period)
        await state.update_data(current_question_index=current_index + 1)
    else:
        # Опрос завершен
        poll_titles = {
            "week1": "первой недели",
            "month1": "первого месяца", 
            "month3": "трёх месяцев"
        }
        
        poll_title = poll_titles.get(period, period)
        completion_message = f"✅ Опрос {poll_title} завершён! Спасибо за ответы."
        
        # Добавляем информацию об отправке администратору
        completion_message += "\n📤 Отчет отправлен администратору."
        
        await message.answer(completion_message)
        
        # Запускаем следующий опрос, если есть
        if next_poll:
            await asyncio.sleep(1)  # Небольшая пауза
            await start_poll(message.from_user.id, message.bot, state, next_poll)
        else:
            await state.clear()


# ---------------- Хэндлер неизвестных команд ----------------
@router.message(F.text.startswith('/help'))
async def handle_unknown_command(message: types.Message):
    """Обработка неизвестных команд."""
    known_commands = [
        '/week1', '/month1', '/month3', 
        '/test', '/test_all', '/cancel', '/status',
        '/last_answers', '/send_reports'
    ]
    
    if message.text not in known_commands:
        await message.answer(
            f"❓ Неизвестная команда: {message.text}\n\n"
            f"📋 <b>Доступные команды:</b>\n"
            f"• /start - Начало работы\n"
            f"• /week1 - Опрос первой недели\n"
            f"• /month1 - Опрос первого месяца\n"
            f"• /month3 - Опрос трёх месяцев\n"
            f"• /test - Тестовый опрос\n"
            f"• /test_all - Отправить все вопросы\n"
            f"• /cancel - Отменить опрос\n"
            f"• /status - Статус\n\n"
            f"<i>Админские команды:</i>\n"
            f"• /last_answers - Посмотреть ответы\n"
            f"• /send_reports - Отправить отчеты",
            parse_mode='HTML'
        )


# ---------------- Дополнительная функция для тестирования ----------------
async def send_test_report_to_admin(bot: Bot):
    """Функция для тестирования отправки отчета администратору"""
    test_answers = [
        "❓ 1️⃣ Как ты оцениваешь свой первый опыт работы в компании (1-5)?\n💬 5 - Отлично!",
        "❓ 2️⃣ Насколько тебе понятны твои обязанности и задачи (1-5)?\n💬 4 - Почти всё понятно",
        "❓ 3️⃣ Насколько ты оцениваешь поддержку со стороны коллег и руководства (1-5)?\n💬 5 - Очень хорошая поддержка"
    ]
    
    await send_to_admin(
        bot=bot,
        user_id=950860793,
        username="test_user",
        full_name="Тестовый Пользователь",
        poll_type="week1",
        answers=test_answers
    )
    print("✅ Тестовый отчет отправлен администратору")