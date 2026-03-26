from model.train_model import train_model
from model.predictor import predict_score
from utils.input_handler import get_student_input
from utils.feedback import give_feedback
from storage.save_data import save_student_record

def main():
    print("🎓 Student Study Analyzer\n")

    model = train_model()

    hours, sessions, planned, completed, difficulty = get_student_input()

    score = predict_score(model, hours, sessions, planned, completed, difficulty)

    message = give_feedback(score)

    save_student_record(hours, sessions, completed, score)

    print(f"\n🎯 Predicted Score: {score}%")
    print(f"💬 Feedback: {message}\n")

    completion_rate = (completed / planned) if planned != 0 else 0

    print(f"\n📊 Completion Rate: {round(completion_rate * 100, 2)}%")

    if completion_rate < 0.5:
        print("⚠️ Low completion rate significantly reduced your score.")

if __name__ == "__main__":
    main()