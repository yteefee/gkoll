from peewee import *
from datetime import datetime

db = SqliteDatabase('askmebot.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = BigIntegerField(unique=True)
    username = CharField(null=True)
    first_name = CharField()
    last_name = CharField(null=True)
    registration_date = DateTimeField(default=datetime.now)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()

class PrivacySettings(BaseModel):
    user = ForeignKeyField(User, backref='privacy_settings', unique=True)
    allow_anonymous_questions = BooleanField(default=True)
    allow_public_answers = BooleanField(default=True)
    notify_new_question = BooleanField(default=True)

class Question(BaseModel):
    from_user = ForeignKeyField(User, backref='sent_questions')
    to_user = ForeignKeyField(User, backref='received_questions')
    text = TextField()
    is_anonymous = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    answered = BooleanField(default=False)
    answer_text = TextField(null=True)
    answer_public = BooleanField(default=False)
    answered_at = DateTimeField(null=True)