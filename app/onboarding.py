from aiogram.types import Message
from aiogram import Bot, Router
from app.request.registered_rq import get_user_name, get_user_number
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime, timedelta
from sqlalchemy import select
import app.storage.models as db
from app.storage.models import async_session
import asyncio

router = Router()

# ====================== FSM ======================
class OnboardingStates(StatesGroup):
    week1 = State()
    month1 = State()
    month3 = State()

# ====================== Данные опросов ======================
polls_data = {
    "week1": {
        "intro_text": """
Привет! 😃

Чтобы тебе было комфортно и успешно в нашей команде, просим уделить пару минут 
и ответить на несколько вопросов о твоей первой неделе. Твое мнение очень важно! 🚀""",
        
        "questions": [
            "1️⃣ Как ты оцениваешь свой первый опыт работы в компании (1-5, где 1 - ужасно, 5 - отлично)?",
            "2️⃣ Насколько тебе понятны твои обязанности и задачи (1-5, где 1 - совсем не понятно, 5 - все абсолютно ясно)?",
            "3️⃣ Как ты оцениваешь поддержку со стороны коллег и руководства (1-5, где 1 - совсем не чувствую поддержки, 5 - чувствую полную поддержку)?"
        ],
        
        "outro_text": """Спасибо за участие в пульс-опросе! Твое мнение важно для нас.

Мы понимаем, что вопросы могут возникать, и адаптация - процесс непростой. Каждый шаг - это опыт. Учись и расти! Мы верим в твой потенциал!
Не бойся задавать вопросы, мы здесь, чтобы помочь!

Твои ответы будут учтены. Мы хотим, чтобы ты чувствовал себя комфортно и уверенно!

Спасибо за вклад! С вопросами - к руководителю или в HR. Мы открыты для общения!"""
    },
    "month1": {
        "intro_text": """
Привет! 👋

Месяц пролетел незаметно! 🗓️ Чтобы узнать, как тебе у нас, просим пройти небольшой опрос. Твои ответы помогут нам сделать твою работу еще лучше! 🚀""",
        
        "questions": [
            "1️⃣ Насколько ты чувствуешь себя частью команды (1-5, где 1 - не чувствую себя частью команды, 5 - чувствую себя полноценным членом команды)?",
            "2️⃣ Насколько тебе интересно выполнять свою работу (1-5, где 1 - совсем не интересно, 5 - очень интересно)?",
            "3️⃣ Насколько ты понимаешь, как твоя работа влияет на общие цели компании (1-5, где 1 - совсем не понимаю, 5 - полностью понимаю)?",
            "4️⃣ Какие цели ты ставишь перед собой на следующий месяц?",
            "5️⃣ Какие ресурсы или помощь тебе необходимы для достижения этих целей?"
        ],
        
        "reminder_text": """
Привет! 👋 Вот и пролетел твой первый месяц работы в нашей компании!

Этот бот здесь, чтобы помочь тебе сориентироваться на этом важном этапе:

•  Время подвести итоги: Подумай о том, чему ты научился за этот месяц. Какие задачи ты успешно выполнил, а что пока вызывает трудности?

•  Вспомни договоренности: Были ли у тебя какие-то конкретные ожидания или договоренности, которые ты хотел бы обсудить? Самое время напомнить о них руководителю!

•  Поговори с руководителем: Самое время запланировать встречу со своим непосредственным руководителем. Расскажи о своих успехах, проблемах и задай вопросы. Открытое общение – ключ к успешной адаптации!

•  Зафиксируй свои цели: Поставь перед собой конкретные цели на следующий месяц. Что ты хочешь улучшить, чему научиться?

Что можно обсудить с руководителем:

•  Твои первые впечатления о работе.
•  Соответствие задач твоим ожиданиям.
•  Необходимость дополнительной помощи или обучения.
•  Твои предложения по улучшению работы.
•  Твои цели на следующий месяц.

Помни, что мы всегда готовы поддержать тебя! Не стесняйся обращаться с любыми вопросами. Удачи! 💪"""
    },
    "month3": {
        "intro_text": """
Привет! 👋

Пролетели 3 месяца с твоего трудоустройства в нашу компанию! Поздравляем с успешным прохождением испытательного срока! 🎉

Этот бот напомнит тебе о важных шагах:""",
        
        "questions": [
            "1️⃣ Оцени свои достижения за 3 месяца",
            "2️⃣ Какие вопросы хочешь обсудить с руководителем?"
        ],
        
        "reminder_text": """•  Оцени свои достижения: Подумай, каких результатов ты достиг за эти 3 месяца. Что получилось хорошо, а над чем еще стоит поработать?

•  Вспомни договорённости: Если в процессе собеседования были договоренности об изменении условий работы (например, повышение заработной платы, изменение графика или должностных обязанностей), сейчас самое время напомнить об этом!

•  Напомни менеджеру и руководителю: Не стесняйся обратиться к своему непосредственному руководителю и менеджеру по персоналу. Напомни им о договоренностях и обсудите следующие шаги. Это нормально!

Рекомендуем:

•  Составить список своих достижений за 3 месяца.
•  Подготовить вопросы, которые тебя интересуют.

Удачи в обсуждении! Мы уверены, что ты успешно пройдешь этот этап!"""
    }
}

# ====================== Временное хранилище ======================
active_polls = {}

# ID администратора (замените на реальный)
ADMIN_ID = 5792104302

# ====================== Запуск опроса (ПРОСТОЙ ВАРИАНТ) ======================
async def start_poll(user_id: int, bot: Bot, poll_type: str):
    """
    Упрощенный запуск опроса - просто отправляем вопросы
    """
    try:
        print(f"🚀 Запуск опроса {poll_type} для пользователя {user_id}")
        
        if poll_type not in polls_data:
            print(f"❌ Неизвестный тип опроса: {poll_type}")
            return

        poll_data = polls_data[poll_type]
        
        # Сохраняем данные опроса
        active_polls[user_id] = {
            "poll_type": poll_type,
            "questions": poll_data["questions"],
            "answers": [],
            "current_question": 0,
            "outro_text": poll_data.get("outro_text", ""),
            "reminder_text": poll_data.get("reminder_text", "")
        }
        
        # Отправляем приветственный текст
        await bot.send_message(user_id, poll_data["intro_text"])
        
        # Отправляем первый вопрос
        await asyncio.sleep(0.5)
        await bot.send_message(user_id, poll_data["questions"][0])
        
        print(f"✅ Опрос {poll_type} начат для пользователя {user_id}")
            
    except Exception as e:
        print(f"[start_poll ERROR] для {user_id}: {e}")
        import traceback
        traceback.print_exc()

# ====================== ХЕНДЛЕРЫ ======================
# Вместо использования FSM, будем хранить состояние в active_polls
@router.message()
async def handle_all_messages(message: Message):
    """
    Обрабатываем ВСЕ сообщения и проверяем, есть ли активный опрос
    """
    user_id = message.from_user.id
    print(f"📨 Получено сообщение от {user_id}: {message.text}")
    
    # Проверяем, есть ли активный опрос для этого пользователя
    if user_id not in active_polls:
        print(f"ℹ️ Нет активного опроса для пользователя {user_id}")
        return  # Не обрабатываем, если нет активного опроса
    
    await process_answer(message)

# ====================== Обработка ответов ======================
async def process_answer(message: Message):
    user_id = message.from_user.id
    user_name_for_admin = message.from_user.username
    bot = message.bot
    
    if user_id not in active_polls:
        return
    
    poll = active_polls[user_id]
    poll_type = poll["poll_type"]
    questions = poll["questions"]
    current_question = poll["current_question"]
    answers = poll["answers"]
    
    print(f"📝 Обработка ответа для опроса {poll_type}, вопрос {current_question + 1}/{len(questions)}")
    
    # Добавляем ответ
    answers.append(message.text)
    print(f"✅ Ответ добавлен: {message.text}")
    
    # Проверяем, есть ли еще вопросы
    if current_question + 1 < len(questions):
        # Обновляем текущий вопрос
        active_polls[user_id]["current_question"] = current_question + 1
        
        # Отправляем следующий вопрос
        next_question = questions[current_question + 1]
        await message.answer(next_question)
        print(f"📨 Отправлен следующий вопрос: {current_question + 2}/{len(questions)}")
    else:
        # Опрос завершен
        print(f"✅ Опрос {poll_type} завершен для пользователя {user_id}")
        
        # Отправляем завершающий текст
        if poll.get("outro_text"):
            await message.answer(poll["outro_text"])
        
        # Отправляем текст-напоминание
        if poll.get("reminder_text"):
            await message.answer(poll["reminder_text"])
        user_name = await get_user_name(user_number=None, user_id=None, telegram_id=user_id)
        user_number = await get_user_number(user_id)
        # Формируем сводку для администратора
        summary_parts = [f"📊 Результаты опроса {poll_type}"
                         f"\nзавершен для пользователя {user_name}"
                         f'\nЮзернейм пользователя: @{user_name_for_admin}'
                         f'\nНомер телефона пользователя: {user_number}'
        ]
        
        for i, (question, answer) in enumerate(zip(questions, answers), 1):
            summary_parts.append(f"\n{i}. {question}\n   Ответ: {answer}")
        
        summary_text = "\n".join(summary_parts)
        
        # Отправляем администратору
        try:
            await bot.send_message(ADMIN_ID, summary_text)
            print(f"📨 Ответы отправлены администратору {ADMIN_ID}")
        except Exception as e:
            print(f"[send_to_admin ERROR] {e}")
        
        # Очищаем данные
        if user_id in active_polls:
            del active_polls[user_id]
            print(f"✅ Данные опроса очищены для пользователя {user_id}")

# ====================== Регистрация пользователя ======================
async def reg_users(
    department_id: int, number: str, name: str, telegram_id: int, bot: Bot
) -> bool:
    """
    Регистрация нового пользователя и запуск опросов
    """
    async with async_session() as session:
        try:
            print(f"📝 Регистрация пользователя: {name}, telegram_id: {telegram_id}")
            
            # Проверка существующего пользователя
            existing_user = await session.scalar(
                select(db.User).where(
                    (db.User.telegram_id == telegram_id) | (db.User.number == number)
                )
            )
            if existing_user:
                print(f"❌ Пользователь уже существует: {telegram_id}")
                return False

            org_id = await session.scalar(
                select(db.Department.organization_id).where(db.Department.id == department_id)
            )
            if not org_id:
                print(f"❌ Отдел не найден: {department_id}")
                return False

            now = datetime.utcnow()
            new_user = db.User(
                user_department_id=department_id,
                user_organization_id=org_id,
                name=name,
                number=number,
                telegram_id=telegram_id,
            )
            history = db.History(
                data_start=now.date().isoformat(),
                data_7=(now + timedelta(days=7)).date().isoformat(),
                data_30=(now + timedelta(days=30)).date().isoformat(),
                data_90=(now + timedelta(days=90)).date().isoformat(),
            )
            new_user.chats.append(history)
            session.add(new_user)
            await session.commit()

            print(f"✅ Пользователь {telegram_id} успешно зарегистрирован")
            
            # 🔥 Автозапуск опросов
            await schedule_polls_for_user(user_id=telegram_id, bot=bot)
            return True
        except Exception as e:
            print(f"[reg_users ERROR] {e}")
            import traceback
            traceback.print_exc()
            return False

# ====================== Планировщик опросов ======================
running_tasks = {}

async def schedule_polls_for_user(user_id: int, bot: Bot, force_restart: bool = False):
    """
    Автозапуск опросов для одного пользователя.
    """
    global running_tasks

    if user_id in running_tasks and not force_restart:
        print(f"ℹ️ Задачи уже запущены для пользователя {user_id}")
        return

    async def run_poll(poll_type: str, delay: int):
        await asyncio.sleep(delay)
        print(f"🚀 Отправка опроса {poll_type} пользователю {user_id}")
        try:
            await start_poll(user_id=user_id, bot=bot, poll_type=poll_type)
        except Exception as e:
            print(f"[run_poll ERROR] {poll_type} для {user_id}: {e}")
            import traceback
            traceback.print_exc()

    # Создаём задачи с разными задержками
    tasks = [
        asyncio.create_task(run_poll("week1", 604800)),    # 10 секунд для тестирования
        asyncio.create_task(run_poll("month1", 2678400)), # 1 день (24 часа)
        asyncio.create_task(run_poll("month3", 7776000)) # 30 дней
    ]
    
    running_tasks[user_id] = tasks
    print(f"✅ Задачи планировщика созданы для пользователя {user_id}")

    # Очистка задач после завершения
    for task in tasks:
        task.add_done_callback(lambda t, uid=user_id: running_tasks.pop(uid, None) if uid in running_tasks else None)

# ====================== Восстановление автозапуска ======================
async def restore_schedules(bot: Bot):
    """
    Восстановление автозапуска опросов для всех пользователей с telegram_id.
    """
    try:
        print("🔄 Восстановление расписаний опросов...")
        
        async with async_session() as session:
            result = await session.execute(
                select(db.User.telegram_id).where(db.User.telegram_id.isnot(None))
            )
            user_ids = result.scalars().all()

        print(f"📋 Найдено пользователей: {len(user_ids)}")
        
        for user_id in user_ids:
            try:
                await schedule_polls_for_user(user_id=user_id, bot=bot, force_restart=True)
                print(f"✅ Восстановлено расписание для пользователя {user_id}")
            except Exception as e:
                print(f"[restore_schedules ERROR] для {user_id}: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"[restore_schedules GLOBAL ERROR] {e}")
        import traceback
        traceback.print_exc()
