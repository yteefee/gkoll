from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("Мой профиль", callback_data="profile")],
        [InlineKeyboardButton("Настройки приватности", callback_data="privacy_settings")],
        [InlineKeyboardButton("Мои вопросы", callback_data="my_questions")],
        [InlineKeyboardButton("Список команд", callback_data="help_command")],
        [InlineKeyboardButton("Как это работает?", callback_data="how_it_works")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_privacy_settings(user_settings):
    keyboard = [
        [
            InlineKeyboardButton(
                f"Анонимные вопросы: {'✅' if user_settings.allow_anonymous_questions else '❌'}",
                callback_data="toggle_anonymous"
            )
        ],
        [
            InlineKeyboardButton(
                f"Публичные ответы: {'✅' if user_settings.allow_public_answers else '❌'}",
                callback_data="toggle_public"
            )
        ],
        [
            InlineKeyboardButton(
                f"Уведомления: {'✅' if user_settings.notify_new_question else '❌'}",
                callback_data="toggle_notify"
            )
        ],
        [InlineKeyboardButton("Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_question_options(question_id):
    keyboard = [
        [
            InlineKeyboardButton("Ответить", callback_data=f"answer_{question_id}"),
            InlineKeyboardButton("Игнорировать", callback_data=f"ignore_{question_id}")
        ],
        [
            InlineKeyboardButton("Ответить публично", callback_data=f"answer_public_{question_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_to_menu():
    keyboard = [
        [InlineKeyboardButton("Назад в меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)