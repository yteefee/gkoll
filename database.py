from models import db, User, Question, PrivacySettings

def create_tables():
    with db:
        db.create_tables([User, Question, PrivacySettings])

def initialize():
    create_tables()