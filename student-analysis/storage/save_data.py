import json

def save_student_record(hours, sessions, completed, score):
    record = {
        "hours": hours,
        "sessions": sessions,
        "completed_pages": completed,
        "predicted_score": score
    }

    with open("storage/students.json", "a") as f:
        json.dump(record, f)
        f.write("\n")