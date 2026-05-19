from datetime import datetime, timezone
from database import db


class Exam(db.Model):

    __tablename__ = "exams"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Links Exam to its Questions; deletes questions when exam is deleted
    questions = db.relationship(
        "Question", backref="exam", lazy=True, cascade="all, delete"
    )
