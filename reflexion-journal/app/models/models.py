from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class AIReflection(db.Model):
    __tablename__ = 'ai_reflection'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'daily' | 'final'
    reflection_id = db.Column(db.Integer, db.ForeignKey('reflection_entry.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'reflection_id': self.reflection_id,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=True)
    profile_picture = db.Column(db.String(300), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'profile_picture': self.profile_picture,
            'email': self.email,
            'is_active': self.is_active,
            'is_new': self.is_new,
            'created_at': self.created_at.isoformat()
        }

class UserDayZero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat()
        }
    
class UserDaysGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    days_ammount = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'days_ammount': self.days_ammount
        }

class UserAppCode(db.Model):
    __tablename__ = 'user_app_code'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'code': self.code,
            'type': self.type,
            'created_at': self.created_at.isoformat()
        }
    
class ReflectionEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_mood = db.Column(db.Text, nullable=False)
    reflection_text = db.Column(db.Text, nullable=False)
    interactions = db.Column(db.Text, nullable=True)
    flashbacks = db.Column(db.Text, nullable=True)
    emotions = db.Column(db.Text, nullable=True)
    friendship_talk = db.Column(db.Text, nullable=True)
    experiments = db.Column(db.Text, nullable=True)
    events = db.Column(db.Text, nullable=True)
    rapid_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_mood': self.user_mood,
            'reflection_text': self.reflection_text,
            'interactions': self.interactions,
            'flashbacks': self.flashbacks,
            'emotions': self.emotions,
            'friendship_talk': self.friendship_talk,
            'experiments': self.experiments,
            'events': self.events,
            'rapid_notes': self.rapid_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }