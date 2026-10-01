from flask import Blueprint, render_template, request
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
    page = request.args.get("page", 1, type=int)
    per_page = 10

    query = Question.query.join(
        WrongQuestion, WrongQuestion.question_id == Question.id
    ).distinct()

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "wrong_questions.html", questions=pagination.items, pagination=pagination
    )
