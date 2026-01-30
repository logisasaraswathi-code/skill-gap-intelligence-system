from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------------------------
# Sample AI Knowledge Base
# ---------------------------

CAREER_SKILLS = {
    "data scientist": ["Python", "Machine Learning", "SQL"],
    "web developer": ["HTML", "CSS", "JavaScript"],
}

QUESTIONS = {
    "Python": [
        {
            "question": "What is the output of print(type([]))?",
            "options": ["list", "<class 'list'>", "array", "tuple"],
            "answer": "<class 'list'>"
        },
        {
            "question": "Which keyword is used to create a function?",
            "options": ["def", "func", "function", "lambda"],
            "answer": "def"
        }
    ],
    "Machine Learning": [
        {
            "question": "What is supervised learning?",
            "options": [
                "Uses labeled data",
                "Uses unlabeled data",
                "No data",
                "Random guessing"
            ],
            "answer": "Uses labeled data"
        },
        {
            "question": "Which algorithm is used for regression?",
            "options": ["Linear Regression", "KNN", "K-Means", "Apriori"],
            "answer": "Linear Regression"
        }
    ],
    "SQL": [
        {
            "question": "Which command is used to fetch data?",
            "options": ["GET", "FETCH", "SELECT", "EXTRACT"],
            "answer": "SELECT"
        },
        {
            "question": "Which SQL clause is used to filter records?",
            "options": ["WHERE", "FROM", "TABLE", "ORDER"],
            "answer": "WHERE"
        }
    ]
}

RECOMMENDATIONS = {
    "Python": [
        "FreeCodeCamp Python Course (YouTube)",
        "W3Schools Python Tutorial"
    ],
    "Machine Learning": [
        "Google ML Crash Course",
        "StatQuest ML Playlist (YouTube)"
    ],
    "SQL": [
        "SQLBolt",
        "W3Schools SQL Tutorial"
    ]
}

# ---------------------------
# Routes
# ---------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Skill Gap Intelligence System is running"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400

    return jsonify({
        "message": "Login successful",
        "email": email
    })


@app.route("/get-questions", methods=["POST"])
def get_questions():
    data = request.json
    career = data.get("career").lower()

    skills = CAREER_SKILLS.get(career)
    if not skills:
        return jsonify({"error": "Career not found"}), 404

    quiz = {}
    for skill in skills:
        quiz[skill] = QUESTIONS.get(skill, [])

    return jsonify({
        "career": career,
        "questions": quiz
    })


@app.route("/submit-answers", methods=["POST"])
def submit_answers():
    data = request.json
    answers = data.get("answers")

    results = {}
    recommendations = {}

    for skill, user_answers in answers.items():
        questions = QUESTIONS.get(skill, [])
        correct = 0

        for i, q in enumerate(questions):
            if user_answers[i] == q["answer"]:
                correct += 1

        score = int((correct / len(questions)) * 100)
        results[skill] = score

        if score < 70:
            recommendations[skill] = RECOMMENDATIONS.get(skill, [])

    return jsonify({
        "skill_levels": results,
        "recommendations": recommendations
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
