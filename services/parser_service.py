import re
from PyPDF2 import PdfReader

QUESTION_PATTERN = re.compile(r"^(Q?\d+)\.", re.IGNORECASE)
OPTION_PATTERN = re.compile(r"^([A-D])\.")
CORRECT_PATTERN = re.compile(r"Correct\s*Answer\s*:\s*([A-D])", re.IGNORECASE)
EXPLANATION_PATTERN = re.compile(r"^Explanation\s*:", re.IGNORECASE)


def parse_questions_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)

    raw_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            raw_text += text + "\n"

    lines = normalize_text(raw_text)

    questions = []
    current = None
    current_option = None
    in_explanation = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # -----------------------------------
        # NEW QUESTION
        # Supports:
        # Q25.
        # 25.
        # -----------------------------------
        if QUESTION_PATTERN.match(line):
            if current:
                questions.append(clean_question(current))
            current = {
                "question": "",
                "A": "",
                "B": "",
                "C": "",
                "D": "",
                "correct": "",
                "explanation": "",
            }

            current_option = None
            in_explanation = False

            # remove question number
            line = QUESTION_PATTERN.sub("", line).strip()

            current["question"] += line + " "

            continue

        if not current:
            continue

        # -----------------------------------
        # OPTIONS
        # -----------------------------------
        option_match = OPTION_PATTERN.match(line)

        if option_match:
            current_option = option_match.group(1)
            option_text = OPTION_PATTERN.sub("", line).strip()
            current[current_option] += option_text + " "
            continue

        # -----------------------------------
        # CORRECT ANSWER
        # -----------------------------------
        correct_match = CORRECT_PATTERN.search(line)

        if correct_match:
            current["correct"] = correct_match.group(1)
            continue

        # -----------------------------------
        # EXPLANATION
        # -----------------------------------
        if EXPLANATION_PATTERN.match(line):
            in_explanation = True
            explanation_text = EXPLANATION_PATTERN.sub("", line).strip()
            current["explanation"] += explanation_text + " "
            continue

        # -----------------------------------
        # APPEND MULTILINE CONTENT
        # -----------------------------------
        if in_explanation:
            current["explanation"] += line + " "
        elif current_option:
            current[current_option] += line + " "
        else:
            current["question"] += line + " "

    # save last question
    if current:
        questions.append(clean_question(current))

    return questions


# -----------------------------------
# HELPERS
# -----------------------------------
def normalize_text(text):
    text = text.replace("•", " ")
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        line = re.sub(r"\s+", " ", line)
        line = line.strip()
        if line:
            cleaned.append(line)
    return cleaned


def clean_question(question):
    for key in question:
        question[key] = re.sub(r"\s+", " ", question[key]).strip()

    return question
