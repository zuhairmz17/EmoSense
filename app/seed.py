from app import db
from app.models import Question
from app.questions_data import QUESTIONS


def seed_questions():
    """Insert the 20 questions, or update them in place so IDs stay stable."""
    for order, (dimension, text) in enumerate(QUESTIONS, start=1):
        q = Question.query.filter_by(question_order=order).first()
        if q is None:
            db.session.add(
                Question(dimension=dimension, question_text=text, question_order=order)
            )
        else:
            q.dimension = dimension
            q.question_text = text
    db.session.commit()