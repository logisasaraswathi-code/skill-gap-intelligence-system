from flask import Flask, redirect, url_for, session, request, render_template_string
from flask_dance.contrib.google import make_google_blueprint, google
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default-secret-key")

# -------------------- GOOGLE OAUTH --------------------
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_url="/login/google/authorized"  # Render will handle the domain automatically
)
app.register_blueprint(google_bp, url_prefix="/login")

# -------------------- HOME / LOGIN --------------------
HOME_HTML = """
<h2>Skill Gap Intelligence System</h2>
{% if not logged_in %}
<a href="{{ url_for('google.login') }}">Login with Google</a>
{% else %}
<p>Welcome, {{ name }} ({{ email }})</p>
<a href="{{ url_for('user_input') }}">Proceed to Skill Input</a><br><br>
<a href="{{ url_for('logout') }}">Logout</a>
{% endif %}
"""

@app.route("/")
def home():
    logged_in = False
    name = email = ""
    if google.authorized:
        resp = google.get("/oauth2/v2/userinfo")
        if resp.ok:
            info = resp.json()
            session["user"] = {"email": info["email"], "name": info["name"]}
            logged_in = True
            name = info["name"]
            email = info["email"]
    return render_template_string(HOME_HTML, logged_in=logged_in, name=name, email=email)

# -------------------- USER INPUT PAGE --------------------
USER_INPUT_HTML = """
<h2>Welcome, {{ user['name'] }}</h2>
<form method="post">
  <label>Student Name:</label><br>
  <input type="text" name="student_name" value="{{ user['name'] }}" required><br><br>

  <label>Skills You Know (comma separated):</label><br>
  <input type="text" name="skills" placeholder="Python, SQL, ML" required><br><br>

  <label>Career Goal:</label><br>
  <input type="text" name="goal" placeholder="AI Engineer" required><br><br>

  <button type="submit">Submit</button>
</form>
"""

@app.route("/input", methods=["GET", "POST"])
def user_input():
    if "user" not in session:
        return redirect("/")
    if request.method == "POST":
        session["student_name"] = request.form["student_name"]
        session["skills"] = [s.strip() for s in request.form["skills"].split(",")]
        session["goal"] = request.form["goal"]
        return redirect("/suggestion")
    return render_template_string(USER_INPUT_HTML, user=session["user"])

# -------------------- AI JOB & SKILL RECOMMENDATION --------------------
@app.route("/suggestion")
def suggestion():
    if "skills" not in session or "goal" not in session:
        return redirect("/input")

    known_skills = session["skills"]
    goal = session["goal"]

    # --- Job suggestions ---
    job_db = {
        "Python": ["Backend Developer", "Data Analyst", "Automation Engineer"],
        "SQL": ["Database Analyst", "Data Engineer"],
        "ML": ["Machine Learning Engineer", "Data Scientist"],
        "AI": ["AI Engineer", "Deep Learning Specialist"],
        "HTML": ["Frontend Developer", "Web Designer"],
        "JavaScript": ["Frontend Developer", "Full Stack Developer"]
    }

    suggested_jobs = set()
    for skill in known_skills:
        suggested_jobs.update(job_db.get(skill, []))

    # --- Skills for career goal ---
    goal_skills_db = {
        "AI Engineer": ["Python", "ML", "Deep Learning", "Data Structures", "SQL"],
        "Data Scientist": ["Python", "ML", "Statistics", "SQL", "Data Visualization"],
        "Backend Developer": ["Python", "Django/Flask", "SQL", "APIs"],
        "Frontend Developer": ["HTML", "CSS", "JavaScript", "React"],
        "Full Stack Developer": ["HTML", "CSS", "JavaScript", "Python", "SQL"]
    }

    required_skills = set(goal_skills_db.get(goal, [])) - set(known_skills)

    # --- Learning platforms ---
    learning_platforms = {
        "Python": "https://www.w3schools.com/python/",
        "ML": "https://www.coursera.org/learn/machine-learning",
        "Deep Learning": "https://www.deeplearning.ai/",
        "SQL": "https://www.w3schools.com/sql/",
        "Data Structures": "https://www.geeksforgeeks.org/data-structures/",
        "Statistics": "https://www.khanacademy.org/math/statistics-probability",
        "Data Visualization": "https://www.datacamp.com/courses/data-visualization",
        "Django/Flask": "https://realpython.com/",
        "HTML": "https://www.w3schools.com/html/",
        "CSS": "https://www.w3schools.com/css/",
        "JavaScript": "https://www.w3schools.com/js/",
        "React": "https://reactjs.org/tutorial/tutorial.html"
    }

    recommended_links = {skill: learning_platforms[skill] for skill in required_skills if skill in learning_platforms}

    html = f"<h2>Hi, {session['student_name']}</h2>"
    html += "<h3>Based on your skills, you can consider these jobs:</h3><ul>"
    for job in suggested_jobs:
        html += f"<li>{job}</li>"
    html += "</ul>"

    if required_skills:
        html += "<h3>Skills you should learn to achieve your goal:</h3><ul>"
        for skill in required_skills:
            link = recommended_links.get(skill, "#")
            html += f"<li>{skill} - <a href='{link}' target='_blank'>Learn Here</a></li>"
        html += "</ul>"
    else:
        html += "<h3>You already have all skills needed for your goal!</h3>"

    html += "<br><a href='/input'>Back to Input Page</a><br>"
    html += "<a href='/logout'>Logout</a>"

    return html

# -------------------- LOGOUT --------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
