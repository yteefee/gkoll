from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from models import User, Question, PrivacySettings
from keyboards import *
import database
from datetime import datetime

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user, created = User.get_or_create(
        user_id=user.id,
        defaults={
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
    )
    
    if created:
        PrivacySettings.create(user=db_user)
    
    welcome_text = (
        "👋 Привет! Я gkoll - бот для анонимных вопросов.\n\n"
        "🔹 Ты можешь получать анонимные вопросы от друзей\n"
        "🔹 Отвечать на них или игнорировать\n"
        "🔹 Настраивать приватность\n\n"
        "Отправь мне команду /help для списка команд"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📝 Список команд:\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Получить справку\n"
        "/ask @username - Задать вопрос пользователю\n"
        "/profile - Посмотреть свой профиль\n"
        "/settings - Настройки приватности\n\n"
        "Просто отправь мне /ask @username и свой вопрос, чтобы задать анонимный вопрос!"
    )
    if update.message:
        await update.message.reply_text(help_text)
    else:
        query = update.callback_query
        await query.edit_message_text(help_text, reply_markup=get_main_menu())

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = User.get(User.user_id == update.effective_user.id)
    questions_received = Question.select().where(Question.to_user == user).count()
    questions_answered = Question.select().where(
        (Question.to_user == user) & (Question.answered == True)
    ).count()
    
    profile_text = (
        f"👤 Твой профиль:\n\n"
        f"🆔 ID: {user.user_id}\n"
        f"👀 Имя: {user.full_name}\n"
        f"📅 Зарегистрирован: {user.registration_date.strftime('%d.%m.%Y')}\n\n"
        f"📥 Получено вопросов: {questions_received}\n"
        f"📤 Ответов дано: {questions_answered}\n\n"
        f"🔗 Твоя ссылка для вопросов: t.me/{(await context.bot.get_me()).username}?start={user.user_id}"
    )
    
    if update.message:
        await update.message.reply_text(profile_text, reply_markup=get_main_menu())
    else:
        query = update.callback_query
        await query.edit_message_text(profile_text, reply_markup=get_main_menu())

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = User.get(User.user_id == update.effective_user.id)
    privacy = PrivacySettings.get(user=user)
    
    settings_text = (
        "⚙️ Настройки приватности:\n\n"
        "Здесь ты можешь настроить, кто и как может с тобой взаимодействовать."
    )
    
    if update.message:
        await update.message.reply_text(settings_text, reply_markup=get_privacy_settings(privacy))
    else:
        query = update.callback_query
        await query.edit_message_text(settings_text, reply_markup=get_privacy_settings(privacy))

# ... (остальные функции остаются без изменений, кроме button_click)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "main_menu":
        await query.edit_message_text(
            "Главное меню:",
            reply_markup=get_main_menu()
        )
    
    elif data == "profile":
        await show_profile(update, context)
    
    elif data == "privacy_settings":
        await show_settings(update, context)
    
    elif data == "toggle_anonymous":
        user = User.get(User.user_id == query.from_user.id)
        privacy = PrivacySettings.get(user=user)
        privacy.allow_anonymous_questions = not privacy.allow_anonymous_questions
        privacy.save()
        
        await query.edit_message_text(
            "Настройки приватности обновлены:",
            reply_markup=get_privacy_settings(privacy)
        )
    
    elif data == "toggle_public":
        user = User.get(User.user_id == query.from_user.id)
        privacy = PrivacySettings.get(user=user)
        privacy.allow_public_answers = not privacy.allow_public_answers
        privacy.save()
        
        await query.edit_message_text(
            "Настройки приватности обновлены:",
            reply_markup=get_privacy_settings(privacy)
        )
    
    elif data == "toggle_notify":
        user = User.get(User.user_id == query.from_user.id)
        privacy = PrivacySettings.get(user=user)
        privacy.notify_new_question = not privacy.notify_new_question
        privacy.save()
        
        await query.edit_message_text(
            "Настройки приватности обновлены:",
            reply_markup=get_privacy_settings(privacy)
        )
    
    elif data == "my_questions":
        user = User.get(User.user_id == query.from_user.id)
        unanswered_questions = Question.select().where(
            (Question.to_user == user) & (Question.answered == False)
        )
        
        if unanswered_questions.count() == 0:
            await query.edit_message_text(
                "У тебя нет неотвеченных вопросов.",
                reply_markup=get_main_menu()
            )
            return
        
        question = unanswered_questions[0]
        question_text = (
            f"❓ Вопрос:\n\n{question.text}\n\n"
            f"📅 Дата: {question.created_at.strftime('%d.%m.%Y %H:%M')}"
        )
        
        await query.edit_message_text(
            question_text,
            reply_markup=get_question_options(question.id)
        )
    
    elif data == "help_command":
        await help_command(update, context)
    
    elif data.startswith("answer_"):
        question_id = int(data.split("_")[1])
        question = Question.get(Question.id == question_id)
        
        context.user_data["current_question"] = question.id
        await query.edit_message_text(
            "Напиши свой ответ на вопрос:",
            reply_markup=get_back_to_menu()
        )
    
    elif data.startswith("answer_public_"):
        question_id = int(data.split("_")[2])
        question = Question.get(Question.id == question_id)
        
        privacy = PrivacySettings.get(user=User.get(User.user_id == query.from_user.id))
        if not privacy.allow_public_answers:
            await query.edit_message_text(
                "Ты запретил публичные ответы в настройках приватности.",
                reply_markup=get_main_menu()
            )
            return
        
        context.user_data["current_question"] = question.id
        context.user_data["answer_public"] = True
        await query.edit_message_text(
            "Напиши свой публичный ответ на вопрос:",
            reply_markup=get_back_to_menu()
        )
    
    elif data.startswith("ignore_"):
        question_id = int(data.split("_")[1])
        question = Question.get(Question.id == question_id)
        question.delete_instance()
        
        await query.edit_message_text(
            "Вопрос удален.",
            reply_markup=get_main_menu()
        )
    
    elif data == "how_it_works":
        how_text = (
            "🤖 Как работает gkoll?\n\n"
            "1. Ты получаешь ссылку, которую можешь отправить друзьям или разместить в соцсетях\n"
            "2. Люди могут задать тебе анонимный вопрос через эту ссылку\n"
            "3. Ты получаешь вопрос и можешь:\n"
            "   - Ответить приватно (только отправителю)\n"
            "   - Ответить публично (в своем профиле)\n"
            "   - Игнорировать вопрос\n\n"
            "⚙️ В настройках приватности ты можешь:\n"
            "- Запретить анонимные вопросы\n"
            "- Запретить публичные ответы\n"
            "- Отключить уведомления о новых вопросах"
        )
        await query.edit_message_text(
            how_text,
            reply_markup=get_main_menu()
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "current_question" in context.user_data:
        question_id = context.user_data["current_question"]
        answer_text = update.message.text
        is_public = context.user_data.get("answer_public", False)
        
        question = Question.get(Question.id == question_id)
        question.answered = True
        question.answer_text = answer_text
        question.answer_public = is_public
        question.answered_at = datetime.now()
        question.save()
        
        # Отправка ответа отправителю вопроса
        if not question.is_anonymous:
            answer_message = (
                f"📩 Ты получил ответ на свой вопрос:\n\n"
                f"❓ Вопрос: {question.text}\n\n"
                f"💬 Ответ: {answer_text}"
            )
            await context.bot.send_message(
                chat_id=question.from_user.user_id,
                text=answer_message
            )
        
        # Очистка контекста
        del context.user_data["current_question"]
        if "answer_public" in context.user_data:
            del context.user_data["answer_public"]
        
        await update.message.reply_text(
            "✅ Ответ сохранен!",
            reply_markup=get_main_menu()
        )
    else:
        await update.message.reply_text(
            "Я не понимаю тебя. Используй команды или кнопки меню.",
            reply_markup=get_main_menu()
        )

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Использование: /ask @username ваш вопрос",
            reply_markup=get_back_to_menu()
        )
        return
    
    target_username = context.args[0].lstrip('@')
    question_text = ' '.join(context.args[1:])
    
    try:
        target_user = User.get(User.username == target_username)
    except User.DoesNotExist:
        await update.message.reply_text(
            "Пользователь не найден. Убедитесь, что он начал работу с ботом.",
            reply_markup=get_back_to_menu()
        )
        return
    
    # Остальная часть функции...

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")
    
    if update.callback_query:
        await update.callback_query.answer("Произошла ошибка. Попробуй еще раз.", show_alert=True)
    elif update.message:
        await update.message.reply_text("Произошла ошибка. Попробуй еще раз.", reply_markup=get_main_menu())