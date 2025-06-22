import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, 
                  user_id INTEGER UNIQUE, 
                  username TEXT, 
                  full_name TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, 
                  user_id INTEGER, 
                  text TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def add_user(user_id: int, username: str, full_name: str):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO users 
                 (user_id, username, full_name) 
                 VALUES (?, ?, ?)''',
              (user_id, username, full_name))
    conn.commit()
    conn.close()

def add_message(user_id: int, text: str):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('''INSERT INTO messages 
                 (user_id, text) 
                 VALUES (?, ?)''',
              (user_id, text))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    
    # Общая статистика
    total_users = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_messages = c.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
    
    # Статистика за сегодня
    active_today = c.execute('''SELECT COUNT(DISTINCT user_id) 
                               FROM messages 
                               WHERE date(created_at) = date('now')''').fetchone()[0]
    
    new_users_today = c.execute('''SELECT COUNT(*) 
                                  FROM users 
                                  WHERE date(created_at) = date('now')''').fetchone()[0]
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_messages': total_messages,
        'active_today': active_today,
        'new_users_today': new_users_today
    }