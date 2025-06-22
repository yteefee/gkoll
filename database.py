from peewee import *
from models import *

db = SqliteDatabase('askmebot.db')

def create_tables():
    with db:
        db.create_tables([User, Question, PrivacySettings])

def initialize():
    create_tables()