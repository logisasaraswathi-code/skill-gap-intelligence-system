from flask import Flask, request, redirect, session, render_template_string

app = Flask(__name__)
app.secret_key = "skill-gap-secret-key"

# -------------------- LOGIN PAGE --------------------
LOGIN_HTML = """
<h2>Skill Gap Intelligence System</h2>

<form method="post">
  <input type="text" name="name" placeholder="Student Name" required><br><br>
  <input type="email" name="email" placeholder="Email (Login)" required><br><br>
  <input type="text" name="goal" placeholder="Career Goal (e.g. AI Engineer)" required><br><br>
  <button type="submit">Login</button>
</form>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = {
            "name": request.form["name"],
            "email": request.form["email"],
            "goal": request.form["goal"]
        }
        return redirect("/dashboard")
    return render_template_string(LOGIN_HTML)

# -------------------- DASHBOARD --------------------
@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect("/")

    return f"""
    <h2>Welcome, {user['name']}</h2>
    <p><b>Email:</b> {user['email']}</p>
    <p><b>Career Goal:</b> {user['goal']}</p>

    <a href="/assessment">Start Skill Self-Assessment</a><br><br>
    <a href="/logout">Logout</a>
    """

# -------------------- SKILL ASSESSMENT --------------------
QUESTIONS = {
    "Python": [
        "What is a list?",
        "What is a function?",
        "What does len() do?"
    ],
    "AI": [
        "What is Machine Learning?",
        "Difference between AI and ML?",
        "What is supervised learning?"
    ]
}

@app.route("/assessment", methods=["GET", "POST"])
def assessment():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        score = 0
        total = len(request.form)

        for ans in request.form.values():
            if ans.strip():
                score += 1

        percentage = int((score / total) * 100)

        session["result"] = percentage
        return redirect("/result")

    html = "<h2>Skill Self-Assessment</h2><form method='post'>"

    for skill, qs in QUESTIONS.items():
        html += f"<h3>{skill}</h3>"
        for q in qs:
            html += f"{q}<br><input name='{q}'><br><br>"

    html += "<button type='submit'>Submit Assessment</button></form>"
    return html

# -------------------- RESULT & AI RECOMMENDATION --------------------
@app.route("/result")
def result():
    if "result" not in session:
        return redirect("/dashboard")

    score = session["result"]
    goal = session["user"]["goal"]

    if score < 40:
        level = "Beginner"
        recommendation = "Start with basics on Python & AI"
    elif score < 70:
        level = "Intermediate"
        recommendation = "Practice projects & improve weak areas"
    else:
        level = "Advanced"
        recommendation = "Go for advanced specialization"

    return f"""
    <h2>Assessment Result</h2>
    <p><b>Skill Level:</b> {level}</p>
    <p><b>Skill Percentage:</b> {score}%</p>

    <h3>AI Recommendation</h3>
    <p>{recommendation}</p>

    <h4>Free Learning Resources</h4>
    <ul>
      <li>Python: https://www.w3schools.com/python/</li>
      <li>AI Basics: https://www.coursera.org/learn/ai-for-everyone</li>
      <li>YouTube: freeCodeCamp</li>
    </ul>

    <a href="/dashboard">Back to Dashboard</a>
    """

# -------------------- LOGOUT --------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
