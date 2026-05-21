import re
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# Matches: Q1. / Q97: / Q1 (with text after) — Q-prefixed questions
Q_PREFIX_PATTERN = re.compile(r"^Q(\d+)[.:]", re.IGNORECASE)
# Matches: 169. Some question text — bare number >= 100 only when text follows on same line
# (avoids matching numbered list items like "1. First IP" or "2. Reliability")
BARE_NUM_PATTERN = re.compile(r"^([1-9]\d{2,})\.\s+\S")
# Matches both "A." and "a)" style options
OPTION_PATTERN = re.compile(r"^([A-Da-d])[.)]\s*")
# Matches "Correct Answer(s): A" or "Correct Answer(s): A, C" or "Correct Answer(s): A and C"
CORRECT_PATTERN = re.compile(
    r"^Correct\s*Answers?\s*:\s*([A-Da-d](?:\s*(?:,|and)\s*[A-Da-d])*)?",
    re.IGNORECASE,
)
EXPLANATION_PATTERN = re.compile(r"^Explanation\s*[:(]", re.IGNORECASE)
INCORRECT_EXPLANATION_PATTERN = re.compile(r"^(Incorrect\s*(Answers?\s*Explained|Explanations?)|Correct\s*Explanation)\s*[:(]", re.IGNORECASE)
# Detects embedded explanation/incorrect-answers block inside an option line
EMBEDDED_EXPLANATION_PATTERN = re.compile(
    r"\s+(Explanation\s*[:(]|Incorrect\s*(Answers?\s*Explained|Explanations?)\s*[:(]|Correct\s*Explanation\s*[:(])",
    re.IGNORECASE,
)


def _is_question_start(line):
    """Return True if line starts a new question."""
    return bool(Q_PREFIX_PATTERN.match(line)) or bool(BARE_NUM_PATTERN.match(line))


def _strip_question_number(line):
    """Remove leading question number from line."""
    line = Q_PREFIX_PATTERN.sub("", line)
    line = re.sub(r"^\d+\.\s*", "", line)
    return line.strip()


def _normalize_letter(letter):
    """Normalize 'a,c' or 'a and c' to 'A,C'. Single letter returns 'A'."""
    if not letter:
        return ""
    letters = re.findall(r"[A-Da-d]", letter)
    return ",".join(sorted(set(l.upper() for l in letters)))


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
    awaiting_correct = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # -----------------------------------
        # NEW QUESTION
        # Supports: Q1. / Q97: / 169. text
        # -----------------------------------
        if _is_question_start(line):
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
            awaiting_correct = False

            line = _strip_question_number(line)
            if line:
                current["question"] += line + " "
            continue

        if not current:
            continue

        # -----------------------------------
        # CORRECT ANSWER — next-line letter
        # e.g. "Correct Answer:" then "C" or "c) AWS SDK"
        # -----------------------------------
        if awaiting_correct:
            # Accept "C", "A, C", "A and C", "C." or "C) full option text"
            bare = re.match(
                r"^([A-Da-d](?:\s*(?:,|and)\s*[A-Da-d])*)[.):]?\s*", line, re.IGNORECASE
            )
            if bare:
                if not current["correct"]:
                    current["correct"] = _normalize_letter(bare.group(1))
            awaiting_correct = False
            if bare:
                continue

        # -----------------------------------
        # CORRECT ANSWER — same-line or trigger
        # e.g. "Correct Answer: C" / "Correct Answer: c) AWS"
        # -----------------------------------
        correct_match = CORRECT_PATTERN.search(line)
        if correct_match:
            letter = correct_match.group(1)
            if letter:
                current["correct"] = _normalize_letter(letter)
            else:
                awaiting_correct = True
            continue

        # -----------------------------------
        # OPTIONS (A./a) B./b) C./c) D./d))
        # -----------------------------------
        option_match = OPTION_PATTERN.match(line)
        if option_match:
            current_option = _normalize_letter(option_match.group(1))
            option_text = OPTION_PATTERN.sub("", line).strip()
            # Split off any embedded explanation block inside the option line
            emb = EMBEDDED_EXPLANATION_PATTERN.search(option_text)
            if emb:
                explanation_part = option_text[emb.start():].strip()
                option_text = option_text[:emb.start()].strip()
                current[current_option] += _dedupe_option_text(option_text) + " "
                in_explanation = True
                current["explanation"] += re.sub(r"^[^:(]+[:(]\s*", "", explanation_part).strip() + " "
            else:
                current[current_option] += _dedupe_option_text(option_text) + " "
            continue

        # -----------------------------------
        # EXPLANATION
        # -----------------------------------
        if EXPLANATION_PATTERN.match(line) or INCORRECT_EXPLANATION_PATTERN.match(line):
            in_explanation = True
            explanation_text = re.sub(r"^[^:(]+[:(]\s*", "", line).strip()
            current["explanation"] += explanation_text + " "
            continue

        # -----------------------------------
        # APPEND MULTILINE CONTENT
        # -----------------------------------
        if in_explanation:
            current["explanation"] += line + " "
        elif current_option:
            current[current_option] += line + " "
        elif current["D"]:  # all options parsed, stray line → explanation
            in_explanation = True
            current["explanation"] += line + " "
        else:
            current["question"] += line + " "

    if current:
        questions.append(clean_question(current))

    return questions


# -----------------------------------
# HELPERS
# -----------------------------------
def _dedupe_option_text(text):
    """Remove immediately repeated phrases, e.g. 'Foo bar Foo bar' -> 'Foo bar'."""
    words = text.split()
    n = len(words)
    for half in range(n // 2, 0, -1):
        if words[:half] == words[half : half * 2]:
            return " ".join(words[:half])
    return text


# Splits a long line at embedded question boundaries
_INLINE_Q_SPLIT = re.compile(r"(?=(?:Q\d+[.:]|[1-9]\d{2,}\.\s+\S))")


def _split_inline_options(line):
    """If a line contains multiple options (A...B...C...D...), split into separate lines."""
    if not OPTION_PATTERN.match(line):
        return [line]
    parts = re.split(r"(?<=\S)\s+(?=[B-Db-d][.)])", line)
    return [p.strip() for p in parts if p.strip()]


def normalize_text(text):
    text = text.replace("•", " ")
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        # If multiple questions are jammed onto one line, split them apart
        parts = _INLINE_Q_SPLIT.split(line)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            # If multiple options are jammed onto one line, split them apart
            for subpart in _split_inline_options(part):
                cleaned.append(subpart)
    return cleaned


def clean_question(question):
    for key in question:
        question[key] = re.sub(r"\s+", " ", question[key]).strip()
    return question


def normalize_pdf(pdf_path):
    """
    Parse any MCQ PDF, deduplicate questions, drop malformed ones,
    and overwrite the file with a clean, uniformly-formatted PDF.

    Standard output format per question:
        Q1. Question text
        A. Option A
        ...
        Correct Answer: X
        Explanation: ...
    """
    questions = parse_questions_from_pdf(pdf_path)

    # Deduplicate (keep first occurrence by question text)
    seen = set()
    unique = []
    for q in questions:
        key = q["question"][:80]
        if key not in seen:
            seen.add(key)
            unique.append(q)

    # Drop questions missing options or correct answer
    valid = [
        q for q in unique if q["A"] and q["B"] and q["C"] and q["D"] and q["correct"]
    ]

    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        "n", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=2
    )
    bold = ParagraphStyle("b", parent=normal, fontName="Helvetica-Bold")

    story = []
    for i, q in enumerate(valid):
        story.append(Paragraph(f"Q{i + 1}. {q['question']}", bold))
        story.append(Spacer(1, 4))
        for letter in ("A", "B", "C", "D"):
            story.append(Paragraph(f"{letter}. {q[letter]}", normal))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"Correct Answer: {q['correct']}", bold))
        if q.get("explanation"):
            story.append(Spacer(1, 2))
            story.append(Paragraph(f"Explanation: {q['explanation']}", normal))
        story.append(Spacer(1, 14))

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    doc.build(story)
