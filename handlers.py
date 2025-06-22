from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from models import User, Question, PrivacySettings
from keyboards import *
from config import ADMIN_IDS
from datetime import datetime, timedelta
import database
from telegram import Update
from telegram.ext import ContextTypes
from models import User, Question, PrivacySettings
from keyboards import get_main_menu, get_privacy_settings

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Доступ запрещён")
        return
    
    await update.message.reply_text(
        "👨‍💻 Админ-панель:",
        reply_markup=get_admin_menu()
    )

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
    else:
        db_user.last_active = datetime.now()
        db_user.save()
    
    await update.message.reply_text(
        "👋 Привет! Я бот для анонимных вопросов.\n\n"
        "🔹 Получай анонимные вопросы\n"
        "🔹 Отвечай или игнорируй\n"
        "🔹 Настраивай приватность",
        reply_markup=get_main_menu()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Список команд:\n\n"
        "/start - Главное меню\n"
        "/help - Помощь\n"
        "/ask @user вопрос - Задать вопрос\n"
        "/profile - Ваш профиль\n"
        "/settings - Настройки\n"
        "/admin - Админ-панель"
    )

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Формат: /ask @username вопрос")
        return
    
    target_username = context.args[0].lstrip('@')
    question_text = ' '.join(context.args[1:])
    
    try:
        target_user = User.get(User.username == target_username)
    except User.DoesNotExist:
        await update.message.reply_text("Пользователь не найден")
        return
    
    sender = update.effective_user
    sender_user, _ = User.get_or_create(
        user_id=sender.id,
        defaults={
            'username': sender.username,
            'first_name': sender.first_name,
            'last_name': sender.last_name
        }
    )
    
    Question.create(
        from_user=sender_user,
        to_user=target_user,
        text=question_text,
        is_anonymous=True
    )
    
    await update.message.reply_text("✅ Вопрос отправлен!", reply_markup=get_main_menu())

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = User.get(User.user_id == update.effective_user.id)
    questions_received = Question.select().where(Question.to_user == user).count()
    questions_answered = Question.select().where(
        (Question.to_user == user) & (Question.answered == True)
    ).count()
    
    profile_text = (
        f"👤 Ваш профиль:\n\n"
        f"ID: {user.user_id}\n"
        f"Имя: {user.full_name}\n"
        f"Дата регистрации: {user.registration_date.strftime('%d.%m.%Y')}\n\n"
        f"Получено вопросов: {questions_received}\n"
        f"Дано ответов: {questions_answered}"
    )
    
    if update.message:
        await update.message.reply_text(profile_text, reply_markup=get_main_menu())
    else:
        query = update.callback_query
        await query.edit_message_text(profile_text, reply_markup=get_main_menu())

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = User.get(User.user_id == update.effective_user.id)
    privacy = PrivacySettings.get(user=user)
    
    if update.message:
        await update.message.reply_text(
            "⚙️ Настройки приватности:",
            reply_markup=get_privacy_settings(privacy)
        )
    else:
        query = update.callback_query
        await query.edit_message_text(
            "⚙️ Настройки приватности:",
            reply_markup=get_privacy_settings(privacy)
        )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "toggle_anonymous":
        await toggle_anonymous(update, context)
    
    elif data == "toggle_notify":
        await toggle_notify(update, context)
    
    # ... остальные обработчики ...

    # Основные кнопки
    if data == "profile":
        await show_profile(update, context)
    elif data == "privacy_settings":
        await show_settings(update, context)
    elif data == "my_questions":
        user = User.get(User.user_id == query.from_user.id)
        question = Question.select().where(
            (Question.to_user == user) & (Question.answered == False)
        ).first()
        
        if not question:
            await query.edit_message_text("🎉 Нет новых вопросов!", reply_markup=get_main_menu())
            return
            
        await query.edit_message_text(
            f"❓ Вопрос:\n\n{question.text}\n\n"
            f"📅 {question.created_at.strftime('%d.%m.%Y %H:%M')}",
            reply_markup=get_question_options(question.id)
        )
    elif data == "help_command":
        await query.edit_message_text(
            "📋 Доступные команды:\n\n"
            "/start - Главное меню\n"
            "/profile - Ваш профиль\n"
            "/settings - Настройки\n"
            "/ask @user вопрос - Задать вопрос\n"
            "/admin - Админ-панель",
            reply_markup=get_main_menu()
        )

    elif data == "how_it_works":
        await query.edit_message_text(
            "🤖 Как это работает?\n\n"
            "1. Делитесь своей ссылкой\n"
            "2. Получаете анонимные вопросы\n"
            "3. Отвечаете или игнорируете\n\n"
            "⚙️ Настройки позволяют ограничить вопросы",
            reply_markup=get_main_menu()
        )
    
    
    # Вопросы
    elif data.startswith("answer_"):
        question_id = int(data.split("_")[1])
        context.user_data["answering"] = question_id
        context.user_data["public"] = False
        await query.edit_message_text("Напишите ответ:", reply_markup=get_back_to_menu())
    elif data.startswith("answer_public_"):
        question_id = int(data.split("_")[2])
        context.user_data["answering"] = question_id
        context.user_data["public"] = True
        await query.edit_message_text("Напишите публичный ответ:", reply_markup=get_back_to_menu())
    elif data.startswith("ignore_"):
        question_id = int(data.split("_")[1])
        Question.delete().where(Question.id == question_id).execute()
        await query.edit_message_text("Вопрос удалён", reply_markup=get_main_menu())
    
    # Админка
    elif data == "admin_stats":
        if is_admin(query.from_user.id):
            stats = {
                'users': User.select().count(),
                'active': User.select().where(User.last_active > datetime.now() - timedelta(days=7)).count(),
                'questions': Question.select().count()
            }
            await query.edit_message_text(
                f"📊 Статистика:\n👥 Пользователей: {stats['users']}\n"
                f"🟢 Активных: {stats['active']}\n❓ Вопросов: {stats['questions']}",
                reply_markup=get_back_to_admin_menu()
            )
    elif data == "admin_users":
        if is_admin(query.from_user.id):
            users = User.select().order_by(User.registration_date.desc()).limit(5)
            text = "Последние 5 пользователей:\n\n" + "\n".join(
                f"👤 {u.full_name} (@{u.username or 'нет'})" for u in users
            )
            await query.edit_message_text(text, reply_markup=get_back_to_admin_menu())
    elif data == "admin_broadcast":
        if is_admin(query.from_user.id):
            context.user_data["broadcasting"] = True
            await query.edit_message_text(
                "✉️ Введите сообщение для рассылки:",
                reply_markup=get_back_to_admin_menu()
            )
    elif data == "admin_panel":
        if is_admin(query.from_user.id):
            await query.edit_message_text(
                "👨‍💻 Админ-панель:",
                reply_markup=get_admin_menu()
            )
    
    # Навигация
    elif data == "main_menu":
        await query.edit_message_text(
            "Главное меню:",
            reply_markup=get_main_menu()
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ответы на вопросы
    if "answering" in context.user_data:
        question = Question.get(Question.id == context.user_data["answering"])
        question.answer_text = update.message.text
        question.answered = True
        question.answer_public = context.user_data["public"]
        question.answered_at = datetime.now()
        question.save()
        
        del context.user_data["answering"]
        del context.user_data["public"]
        
        await update.message.reply_text("✅ Ответ сохранён!", reply_markup=get_main_menu())
        return
    
    # Рассылка
    if context.user_data.get("broadcasting"):
        if is_admin(update.effective_user.id):
            results = {'success': 0, 'failed': 0}
            for user in User.select():
                try:
                    await context.bot.send_message(user.user_id, text=update.message.text)
                    results['success'] += 1
                except:
                    results['failed'] += 1
            del context.user_data["broadcasting"]
            await update.message.reply_text(
                f"📢 Рассылка завершена:\n✅ {results['success']}\n❌ {results['failed']}",
                reply_markup=get_admin_menu()
            )
        return
    
    await update.message.reply_text(
        "Используйте кнопки меню",
        reply_markup=get_main_menu()
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error = str(context.error)
    print(f"Ошибка: {error}")
    
    if update.callback_query:
        await update.callback_query.answer("Ошибка. Попробуйте снова.", show_alert=True)
    elif update.message:
        await update.message.reply_text(
            "⚠️ Произошла ошибка",
            reply_markup=get_main_menu()
        )
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Формат: /ask @username вопрос")
        return
    
    target_username = context.args[0].lstrip('@')
    question_text = ' '.join(context.args[1:])
    
    try:
        target_user = User.get(User.username == target_username)
    except User.DoesNotExist:
        await update.message.reply_text("❌ Пользователь не найден")
        return
    
    # Проверка настроек приватности
    privacy = PrivacySettings.get_or_none(user=target_user)
    if not privacy:
        privacy = PrivacySettings.create(user=target_user)
    
    if not privacy.allow_anonymous_questions:
        await update.message.reply_text("❌ Этот пользователь запретил анонимные вопросы")
        return
    
    # Создание вопроса
    sender = update.effective_user
    sender_user, _ = User.get_or_create(
        user_id=sender.id,
        defaults={'username': sender.username, 'first_name': sender.first_name, 'last_name': sender.last_name}
    )
    
    Question.create(
        from_user=sender_user,
        to_user=target_user,
        text=question_text,
        is_anonymous=True,
        created_at=datetime.now()
    )
    
    # Отправка уведомления получателю
    if privacy.notify_new_question:
        try:
            await context.bot.send_message(
                chat_id=target_user.user_id,
                text=f"📩 Новый анонимный вопрос!\n\n{question_text}\n\n"
                     f"Ответьте через меню 'Мои вопросы'",
                reply_markup=get_main_menu()
            )
        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")
    
    await update.message.reply_text("✅ Ваш вопрос отправлен!", reply_markup=get_main_menu())

async def toggle_anonymous(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = User.get(User.user_id == query.from_user.id)
    privacy = PrivacySettings.get(user=user)
    privacy.allow_anonymous_questions = not privacy.allow_anonymous_questions
    privacy.save()
    
    await query.edit_message_text(
        "⚙️ Настройки обновлены:",
        reply_markup=get_privacy_settings(privacy)
    )

async def toggle_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = User.get(User.user_id == query.from_user.id)
    privacy = PrivacySettings.get(user=user)
    privacy.notify_new_question = not privacy.notify_new_question
    privacy.save()
    
    await query.edit_message_text(
        "⚙️ Настройки обновлены:",
        reply_markup=get_privacy_settings(privacy)
    )