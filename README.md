# 📝 Flask Exam Creator App

A web application that lets you **upload PDF exam files**, automatically parse multiple-choice questions, and take interactive practice exams — with progress tracking and wrong-answer review.

---

## 🚀 Features

- 📄 **PDF Upload & Parsing** — Upload MCQ-formatted PDFs; questions are extracted automatically
- 🎯 **Flexible Exam Modes** — Practice with all questions, only wrong answers, or unanswered ones
- 📊 **Score & Results** — Instant feedback with pass/fail (≥70% to pass)
- 🔁 **Wrong Question Tracking** — Revisit questions you got wrong
- 📈 **Dashboard** — Overview of exam history and performance
- 🗃️ **SQLite Database** — Lightweight, zero-config persistence

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) | Python 3.13 |
| ![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white) | Flask 3.0 — web framework |
| ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white) | Flask-SQLAlchemy 3.1 — ORM |
| ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white) | SQLite — database |
| ![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white) | Tailwind CSS — styling |
| ![PyPDF2](https://img.shields.io/badge/PyPDF2-FF0000?logo=adobeacrobatreader&logoColor=white) | PyPDF2 3.0 — PDF parsing |

---

## 📁 Project Structure

```
flask_exam_creator_app/
├── app.py                  # App factory & entry point
├── database.py             # SQLAlchemy db instance
├── requirements.txt        # Python dependencies
├── tailwind.config.js      # Tailwind configuration
│
├── models/
│   ├── exam.py             # Exam model
│   ├── question.py         # Question model
│   ├── exam_result.py      # ExamResult model
│   ├── question_attempt.py # QuestionAttempt model
│   └── wrong_question.py   # WrongQuestion model
│
├── routes/
│   ├── main_routes.py      # Index / home
│   ├── upload_routes.py    # PDF upload & parsing
│   ├── exam_routes.py      # Exam taking & submission
│   └── dashboard_routes.py # Dashboard & stats
│
├── services/
│   └── parser_service.py   # PDF → questions parser (regex)
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── exams.html
│   ├── exam.html
│   ├── result.html
│   ├── dashboard.html
│   └── wrong_questions.html
│
├── static/
│   ├── tailwind.css
│   └── images/
│
└── uploads/                # Uploaded PDF files
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd flask_exam_creator_app
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
```

### 5. Run the app
```bash
python app.py
```

The app will be available at `http://127.0.0.1:5000`.

---

## 📄 PDF Format

The parser expects PDFs with questions in this format:

```
Q1. What is AWS?
A. A cloud provider
B. A database
C. A programming language
D. An operating system
Correct Answer: A
Explanation: AWS (Amazon Web Services) is a cloud computing platform.
```

---

## 🎮 How to Use

1. **Upload** a PDF via the Upload page
2. **Select an exam** from the Exams list
3. **Choose exam mode**: All questions / Wrong answers only / Unanswered only
4. **Set question count** and start the exam
5. **Submit** to see your score and review results
6. **Track progress** on the Dashboard

---

## 📦 Dependencies

```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
PyPDF2==3.0.1
python-dotenv
```

---

## 📜 License

MIT
