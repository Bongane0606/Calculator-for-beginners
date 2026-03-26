import pandas as pd

def load_data():
    data = {
        "hours_studied": [1, 2, 3, 4, 5, 6, 7, 8],
        "study_sessions": [1, 1, 2, 2, 3, 3, 4, 4],
        "completion_rate": [0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95],
        "difficulty": [1, 1, 2, 2, 2, 3, 3, 3],
        "score": [35, 45, 55, 60, 70, 75, 85, 92]
    }

    return pd.DataFrame(data)