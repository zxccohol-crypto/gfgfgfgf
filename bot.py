"""
Telegram Bot - З підтримкою Webhook для Render.com
"""

import logging
import random
import string
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from flask import Flask, request
import asyncio
from threading import Thread

# ==================== CONFIG ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # 🔑 Обов'язково вказати в Render Environment Variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")  # Буде типу: https://твоя-назва.onrender.com
PORT = int(os.getenv("PORT", 10000))  # Render автоматично встановлює PORT

MANAGER_USERNAME = "@BTCRedoManager"
ADMIN_USER_ID = 123456789

# Тексти для повідомлень
WELCOME_TEXT = """⚜️𝐁𝐓𝐂𝐑𝐞𝐝𝐨

Статус: НОВИЧОК

ID: {user_id} | Комиссия: 50%

💼 Общая сумма закрытий: 0$

👥 Закрыто: сегодня — 0 | неделя — 0 | всего — 0

Выберите раздел ниже 👇"""

TEXT_BUTTON_1 = """Профессиональное пространство для специалистов по отмене BTC-транзакций.

Здесь работают дисциплина, качество и результат. Если вы не готовы соблюдать регламент, внимательно читать инструкции и держать коммуникацию на уровне — эта платформа не для вас.

Мы даём стабильный поток клиентов и набор инструментов. Ваша задача — качественно обрабатывать трафик, следовать правилам и доводить процесс до результата.

С чего начать:

- Изучите рабочий процесс: «Информация о работе»
- Освойте методику по шагам: «Руководство»
- Обязательно протестируйте процедуру на своих тест-кошельках

После теста можно приступать к работе.

Если материалы изучены и тестирование пройдено — свяжитесь с тимлидом, чтобы получить доступ и стартовать.
"""

TEXT_BUTTON_2 = """📚 Руководства

Изучи оба гайда и выбери тот, который удобнее именно тебе.

- Обязательно проверь отмену транзакций на своих кошельках
- Отдельно изучи гайд по обработке — он сильно упрощает работу и повышает эффективность

Если появились вопросы — пиши тимлиду в «Контактах»."""

TEXT_BUTTON_3 = """📌 Правила

▪️ Запрещена реклама сторонних проектов
▪️ Запрещена дезинформация о проекте и его деятельности
▪️ Запрещена передача рабочих инструментов и конфиденциальной информации третьим лицам
▪️ Запрещено игнорирование требований и инструкций тимлида
▪️ Запрещено нарушение финансовой дисциплины и несвоевременная отчётность
"""

TEXT_BUTTON_4 = """🔒 Чат команды временно недоступен

Чтобы получить доступ, повысь статус.

Твой статус: НОВИЧОК
Требуемый статус: ОПЫТНЫЙ"""

TEXT_BUTTON_5 = """Контакты

Если возникли вопросы по процессу, сложности или нужна дополнительная информация — напиши тимлиду.

👨🏻‍💻 Тимлид поможет разобраться в деталях, даст необходимые инструкции и поддержит на каждом этапе."""

# Посилання на Telegraph
TELEGRAPH_LINK_1_1 = "https://telegra.ph/Informaciya-o-rabote-01-19"
TELEGRAPH_LINK_1_2 = "https://telegra.ph/MANUAL-OTMENA-TRANZAKCII-S-BITKOINOM-01-19"
TELEGRAPH_LINK_2_1 = "https://telegra.ph/MANUAL-OTMENA-TRANZAKCII-S-BITKOINOM-01-19"
TELEGRAPH_LINK_2_2 = "https://telegra.ph/Rukovodstvo-dlya-menedzhera-po-obrabotke-mamontov-01-19"

# ==================== END CONFIG ====================

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app для webhook
app = Flask(__name__)

# Створюємо Application одразу
application = Application.builder().token(BOT_TOKEN).build() if BOT_TOKEN else None


def generate_user_id() -> str:
    """Генерує випадковий короткий ID користувача (6 символів)"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(6))


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Створює головну клавіатуру з 5 кнопками"""
    keyboard = [
        [InlineKeyboardButton("Основная информация", callback_data="btn_1")],
        [InlineKeyboardButton("Руководство", callback_data="btn_2")],
        [InlineKeyboardButton("Правила", callback_data="btn_3")],
        [InlineKeyboardButton("Чат команды", callback_data="btn_4")],
        [InlineKeyboardButton("Контакты", callback_data="btn_5")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_keyboard_button_1() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Информация о работе", url=TELEGRAPH_LINK_1_1)],
        [InlineKeyboardButton("Руководство", url=TELEGRAPH_LINK_1_2)],
        [InlineKeyboardButton("Связаться с тимлидом", url=f"https://t.me/{MANAGER_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_keyboard_button_2() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Руководство по отмене с пк", url=TELEGRAPH_LINK_2_1)],
        [InlineKeyboardButton("Руководство по обработке мамонта", url=TELEGRAPH_LINK_2_2)],
        [InlineKeyboardButton("Связаться с тимлидом", url=f"https://t.me/{MANAGER_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_keyboard_button_3() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_keyboard_button_4() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_keyboard_button_5() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Связаться с тимлидом", url=f"https://t.me/{MANAGER_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник команди /start"""
    user_id = generate_user_id()
    context.user_data['user_id'] = user_id
    
    welcome_message = WELCOME_TEXT.format(user_id=user_id)
    keyboard = get_main_keyboard()
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=keyboard
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник натискань на кнопки"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_main":
        user_id = context.user_data.get('user_id', generate_user_id())
        welcome_message = WELCOME_TEXT.format(user_id=user_id)
        keyboard = get_main_keyboard()
        await query.edit_message_text(
            welcome_message,
            reply_markup=keyboard
        )
        return
    
    elif data == "btn_1":
        keyboard = get_keyboard_button_1()
        await query.edit_message_text(
            TEXT_BUTTON_1,
            reply_markup=keyboard
        )
    
    elif data == "btn_2":
        keyboard = get_keyboard_button_2()
        await query.edit_message_text(
            TEXT_BUTTON_2,
            reply_markup=keyboard
        )
    
    elif data == "btn_3":
        keyboard = get_keyboard_button_3()
        await query.edit_message_text(
            TEXT_BUTTON_3,
            reply_markup=keyboard
        )
    
    elif data == "btn_4":
        keyboard = get_keyboard_button_4()
        await query.edit_message_text(
            TEXT_BUTTON_4,
            reply_markup=keyboard
        )
    
    elif data == "btn_5":
        keyboard = get_keyboard_button_5()
        await query.edit_message_text(
            TEXT_BUTTON_5,
            reply_markup=keyboard
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник помилок"""
    logger.error(f"Update {update} caused error {context.error}")


# ==================== FLASK ROUTES ====================

@app.route('/')
def index():
    """Health check endpoint"""
    return 'Bot is running! ✅', 200


@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint для отримання оновлень від Telegram"""
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(application.process_update(update))
    return 'ok'


# ==================== MAIN ====================

async def setup_webhook():
    """Налаштування webhook"""
    if not application:
        logger.error("❌ Application не створено - перевір BOT_TOKEN!")
        return
    
    if not WEBHOOK_URL:
        logger.error("❌ WEBHOOK_URL не встановлено!")
        return
    
    # Додаємо обробники
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)
    
    # Ініціалізуємо бота
    await application.initialize()
    await application.start()
    
    webhook_url = f"{WEBHOOK_URL}/webhook"
    await application.bot.set_webhook(url=webhook_url)
    logger.info(f"🚀 Бот запущено на webhook режимі!")
    logger.info(f"🌐 Webhook URL: {webhook_url}")
    logger.info(f"🔌 Port: {PORT}")


def main() -> None:
    """Головна функція - для локального запуску"""
    # Перевірка наявності токена
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не встановлено!")
        return
    
    if not WEBHOOK_URL:
        logger.error("❌ WEBHOOK_URL не встановлено!")
        return
    
    # Налаштовуємо webhook
    asyncio.run(setup_webhook())
    
    # Запускаємо Flask
    app.run(host='0.0.0.0', port=PORT)


if __name__ == '__main__':
    main()
