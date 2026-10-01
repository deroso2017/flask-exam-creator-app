from database import db
from datetime import datetime, timezone


class InterestingQuestion(db.Model):
    __tablename__ = "interesting_questions"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
