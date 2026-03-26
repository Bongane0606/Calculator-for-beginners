from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from data.dataset import load_data

def train_model():
    df = load_data()

    X = df[[
        "hours_studied",
        "study_sessions",
        "completion_rate",
        "difficulty"
    ]]
    
    y = df["score"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = LinearRegression()
    model.fit(X_train, y_train)

    return model