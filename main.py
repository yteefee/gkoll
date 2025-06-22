from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers import (
    start, help_command, ask_question, 
    show_profile, show_settings, 
    admin_panel, button_click, 
    handle_message, error_handler
)
from database import initialize
import config
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    initialize()
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ask", ask_question))
    app.add_handler(CommandHandler("profile", show_profile))
    app.add_handler(CommandHandler("settings", show_settings))
    app.add_handler(CommandHandler("admin", admin_panel))
    
    # Обработчики
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    app.run_polling()

if __name__ == '__main__':
    main()