import re
from PyPDF2 import PdfReader


def parse_questions_from_pdf(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        text += page.extract_text()

    blocks = re.split(r"Q\d+\.", text)

    questions = []

    for block in blocks:

        if not block.strip():
            continue

        try:
            question = re.search(r"^(.*?)A\.", block, re.S).group(1).strip()
            option_a = re.search(r"A\.(.*?)B\.", block, re.S).group(1).strip()
            option_b = re.search(r"B\.(.*?)C\.", block, re.S).group(1).strip()
            option_c = re.search(r"C\.(.*?)D\.", block, re.S).group(1).strip()
            option_d = (
                re.search(r"D\.(.*?)Correct Answer:", block, re.S).group(1).strip()
            )

            correct = re.search(r"Correct Answer:\s*([A-D])", block).group(1)

            explanation = (
                re.search(r"Explanation:\s*(.*)", block, re.S).group(1).strip()
            )

            questions.append(
                {
                    "question": question,
                    "A": option_a,
                    "B": option_b,
                    "C": option_c,
                    "D": option_d,
                    "correct": correct,
                    "explanation": explanation,
                }
            )

        except Exception:
            continue

    return questions
