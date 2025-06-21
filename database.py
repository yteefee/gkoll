import os
import psycopg2
from psycopg2 import sql
from contextlib import contextmanager

# Подключение к базе
@contextmanager
def get_db_connection():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_db_cursor():
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            yield cur
            conn.commit()
        finally:
            cur.close()

# Инициализация БД
def init_db():
    with get_db_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

# Операции с пользователями
def add_user(user_id: int, username: str, full_name: str):
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO users (user_id, username, full_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, username, full_name))

# Операции с сообщениями
def add_message(user_id: int, text: str):
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO messages (user_id, text)
            VALUES (%s, %s)
        """, (user_id, text))

# Статистика
def get_stats():
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM messages")
        total_messages = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM users
            WHERE created_at::date = CURRENT_DATE
        """)
        new_users_today = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(DISTINCT user_id) FROM messages
            WHERE created_at::date = CURRENT_DATE
        """)
        active_today = cur.fetchone()[0]

        return {
            'total_users': total_users,
            'total_messages': total_messages,
            'new_users_today': new_users_today,
            'active_today': active_today
        }