from datetime import datetime, timezone
from database import db


class QuestionAttempt(db.Model):
    __tablename__ = "question_attempts"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(
        db.Integer, db.ForeignKey("questions.id")  # must match __tablename__
    )

    is_correct = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
