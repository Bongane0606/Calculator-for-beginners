import json
from pathlib import Path

def save_student_record(hours, sessions, completed, score):
    record = {
        "hours": hours,
        "sessions": sessions,
        "completed_pages": completed,
        "predicted_score": score
    }

    output_file = Path(__file__).resolve().parent / "students.json"

    with output_file.open("a") as f:
        json.dump(record, f)
        f.write("\n")
