def predict_score(model, hours, sessions, planned, completed, difficulty):

    # Completion rate
    if planned == 0:
        completion_rate = 0
    else:
        completion_rate = completed / planned

    # Base score from effort
    base_score = (hours * 2) + (sessions * 3)

    # Completion impact (VERY IMPORTANT)
    completion_score = completion_rate * 50  # strong influence

    # Difficulty adjustment
    difficulty_bonus = difficulty * 5

    # Combine
    score = base_score + completion_score + difficulty_bonus

    # 🚨 REALISTIC PENALTIES
    if completion_rate < 0.5:
        score -= 20  # heavy penalty

    if completion_rate < 0.3:
        score -= 30  # very poor performance

    if difficulty == 3 and completion_rate < 0.5:
        score -= 10  # tried hard but failed → penalty

    # Clamp score between 0–100
    score = max(0, min(score, 100))

    return round(score, 2)