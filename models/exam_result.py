from datetime import datetime, timezone
from database import db


class ExamResult(db.Model):

    __tablename__ = "exam_result"

    id = db.Column(db.Integer, primary_key=True)
    exam_type = db.Column(db.String(50))
    total_questions = db.Column(db.Integer)
    correct_answers = db.Column(db.Integer)
    wrong_answers = db.Column(db.Integer)
    score = db.Column(db.Float)
    passed = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
