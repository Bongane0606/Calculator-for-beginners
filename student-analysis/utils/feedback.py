def give_feedback(score):
    if score >= 80:
        return "🔥 Excellent! You studied effectively and completed your goals."
    elif score >= 65:
        return "💪 Good effort, but improve completion."
    elif score >= 50:
        return "⚠️ You studied, but didn’t complete enough work."
    else:
        return "❌ Poor performance. Focus on finishing what you start."