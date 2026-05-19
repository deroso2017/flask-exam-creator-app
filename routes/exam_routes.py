import random
from flask import Blueprint, render_template, request
from database import db
from models.exam import Exam
from models.question import Question
from models.exam_result import ExamResult
from models.wrong_question import WrongQuestion
from models.question_attempt import QuestionAttempt

exam_bp = Blueprint("exam", __name__)


@exam_bp.route("/exams", methods=["GET", "POST"])
def exams():

    if request.method == "GET":
        exams_list = Exam.query.all()
        return render_template("exams.html", exams=exams_list)

    exam_id = request.form.get("exam_id")
    exam_type = request.form.get("exam_type", "all")
    count = int(request.form.get("count", 10))

    questions = []

    # BASE QUERY (by exam)
    base_query = Question.query.filter_by(exam_id=exam_id)

    # EXAM TYPE FILTER
    if exam_type == "wrong":
        # gets a list of unique question IDs from the WrongQuestion table
        wrong_ids = (
            db.session.query(WrongQuestion.question_id).distinct().all()
        )  # distinct(): removes duplicates (keeps each ID only once)

        wrong_ids = [w[0] for w in wrong_ids]

        questions = base_query.filter(Question.id.in_(wrong_ids)).all()

    elif exam_type == "unanswered":

        answered_ids = db.session.query(QuestionAttempt.question_id).distinct().all()

        answered_ids = [a[0] for a in answered_ids]

        questions = base_query.filter(~Question.id.in_(answered_ids)).all()

    else:
        questions = base_query.all()

    # SAFETY CHECK
    if not questions:
        return render_template("exam.html", questions=[], exam_type=exam_type)

    # LIMIT QUESTIONS
    if len(questions) > count:
        questions = random.sample(questions, count)

    return render_template("exam.html", questions=questions, exam_type=exam_type)


@exam_bp.route("/submit_exam", methods=["POST"])
def submit_exam():

    question_ids = request.form.getlist("question_ids")

    correct = 0
    wrong = 0

    for qid in question_ids:

        question = Question.query.get(int(qid))
        if not question:
            continue

        selected = request.form.get(f"question_{qid}")

        # handle unanswered questions
        if not selected:
            wrong += 1

            db.session.add(QuestionAttempt(question_id=question.id, is_correct=False))
            continue

        is_correct = selected == question.correct_answer

        if is_correct:
            correct += 1
        else:
            wrong += 1

            db.session.add(
                WrongQuestion(question_id=question.id, selected_answer=selected)
            )

        # record attempt (always)
        db.session.add(QuestionAttempt(question_id=question.id, is_correct=is_correct))

    total = len(question_ids)

    score = round((correct / total) * 100, 2) if total else 0
    passed = score >= 70

    exam_result = ExamResult(
        exam_type=request.form.get("exam_type"),
        total_questions=total,
        correct_answers=correct,
        wrong_answers=wrong,
        score=score,
        passed=passed,
    )

    db.session.add(exam_result)
    db.session.commit()

    return render_template(
        "result.html", score=score, passed=passed, correct=correct, wrong=wrong
    )
