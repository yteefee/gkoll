from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu():
    buttons = [
        [InlineKeyboardButton("👤 Мой профиль", callback_data="profile")],
        [InlineKeyboardButton("⚙️ Настройки приватности", callback_data="privacy_settings")],
        [InlineKeyboardButton("📩 Мои вопросы", callback_data="my_questions")],
        [InlineKeyboardButton("📋 Список команд", callback_data="help_command")],
        [InlineKeyboardButton("❓ Как это работает?", callback_data="how_it_works")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_privacy_settings(privacy):
    buttons = [
        [
            InlineKeyboardButton(
                f"Анонимные вопросы: {'✅ Вкл' if privacy.allow_anonymous_questions else '❌ Выкл'}",
                callback_data="toggle_anonymous"
            )
        ],
        [
            InlineKeyboardButton(
                f"Уведомления: {'✅ Вкл' if privacy.notify_new_question else '❌ Выкл'}",
                callback_data="toggle_notify"
            )
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_question_options(question_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ Ответить", callback_data=f"answer_{question_id}"),
            InlineKeyboardButton("❌ Удалить", callback_data=f"ignore_{question_id}")
        ],
        [
            InlineKeyboardButton("📢 Ответить публично", callback_data=f"answer_public_{question_id}")
        ]
    ])

def get_admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="main_menu")]
    ])

def get_back_to_admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ])

def get_back_to_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ])