def get_student_input():
    print("\n📚 Enter Study Details:\n")

    hours = float(input("Hours studied: "))
    sessions = int(input("Number of study sessions: "))

    planned = int(input("Pages/chapters planned: "))
    completed = int(input("Pages/chapters completed: "))

    print("\n📊 Study Difficulty Level:")
    print("1 - Struggled")
    print("2 - Moderate")
    print("3 - Mastered")

    difficulty = int(input("Select level (1/2/3): "))

    return hours, sessions, planned, completed, difficulty