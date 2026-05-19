from database import db
from datetime import datetime, timezone


class WrongQuestion(db.Model):
    __tablename__ = "wrong_questions"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(
        db.Integer, db.ForeignKey("questions.id")  # ✅ MUST be plural
    )

    selected_answer = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
