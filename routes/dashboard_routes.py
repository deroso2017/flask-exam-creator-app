from flask import Blueprint, render_template
from models.exam_result import ExamResult
from models.question import Question
from models.wrong_question import WrongQuestion

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    results = ExamResult.query.order_by(ExamResult.created_at.desc()).all()
    return render_template("dashboard.html", results=results)


@dashboard_bp.route("/wrong_questions")
def wrong_questions():

    wrongs = WrongQuestion.query.all()
    questions = []

    for w in wrongs:
        question = Question.query.get(w.question_id)

        if question:
            questions.append(question)

    return render_template("wrong_questions.html", questions=questions)
