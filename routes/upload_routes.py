import os
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from werkzeug.utils import secure_filename
from database import db
from models.exam import Exam
from models.question import Question
from services.parser_service import parse_questions_from_pdf

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["GET", "POST"])
def upload_pdf():

    if request.method == "POST":

        pdf = request.files.get("pdf")

        if not pdf:
            flash("Please upload a PDF.")
            return redirect(request.url)

        filename = secure_filename(pdf.filename)

        upload_dir = "uploads"
        os.makedirs(
            upload_dir, exist_ok=True
        )  # exist_ok=True → don’t throw an error if the folder already exists

        filepath = os.path.join(upload_dir, filename)
        pdf.save(filepath)

        title = request.form.get("title")

        # CREATE EXAM FIRST
        exam = Exam(title=title)

        db.session.add(exam)
        db.session.flush()  # gives exam.id without full commit

        # PARSE PDF
        questions = parse_questions_from_pdf(filepath)

        # CREATE QUESTIONS
        for q in questions:
            question = Question(
                exam_id=exam.id,
                question=q["question"],
                option_a=q["A"],
                option_b=q["B"],
                option_c=q["C"],
                option_d=q["D"],
                correct_answer=q["correct"],
                explanation=q["explanation"],
            )

            db.session.add(question)

        # FINAL COMMIT
        db.session.commit()

        flash(f"{len(questions)} questions imported.")

        return redirect(url_for("main.index"))

    return render_template("upload.html")
