from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    mood_entries = db.relationship(
        "MoodEntry", backref="user", cascade="all, delete-orphan", lazy="dynamic"
    )
    assessments = db.relationship(
        "AssessmentAttempt", backref="user", cascade="all, delete-orphan", lazy="dynamic"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class MoodEntry(db.Model):
    __tablename__ = "mood_entries"
    __table_args__ = (
        db.CheckConstraint("intensity >= 1 AND intensity <= 5", name="ck_mood_intensity"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    mood = db.Column(db.String(20), nullable=False)
    intensity = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    dimension = db.Column(db.String(30), nullable=False)
    question_text = db.Column(db.String(255), nullable=False)
    question_order = db.Column(db.Integer, unique=True, nullable=False)


class AssessmentAttempt(db.Model):
    __tablename__ = "assessment_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    overall_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    answers = db.relationship(
        "AssessmentAnswer", backref="attempt", cascade="all, delete-orphan"
    )


class AssessmentAnswer(db.Model):
    __tablename__ = "assessment_answers"
    __table_args__ = (
        db.CheckConstraint("answer_value >= 1 AND answer_value <= 5", name="ck_answer_value"),
        db.UniqueConstraint("assessment_id", "question_id", name="uq_attempt_question"),
    )

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("assessment_attempts.id"), nullable=False, index=True
    )
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    answer_value = db.Column(db.Integer, nullable=False)

    question = db.relationship("Question")