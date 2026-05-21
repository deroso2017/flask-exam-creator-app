from database import db


class Question(db.Model):

    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)

    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text)
    option_b = db.Column(db.Text)
    option_c = db.Column(db.Text)
    option_d = db.Column(db.Text)

    correct_answer = db.Column(db.String(20))
    difficulty = db.Column(db.String(10))
    explanation = db.Column(db.Text)
