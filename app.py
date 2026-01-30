from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)
app.secret_key = "your-secret-key"

# ------------------ TEMP STORAGE (ADMIN DATA) ------------------
students_data = []

# ------------------ PREDEFINED CAREER GOALS ------------------
CAREER_GOALS = [
    "AI Engineer",
    "Data Scientist",
    "Web Developer",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer"
]

# ------------------ INPUT PAGE ------------------
INPUT_HTML = """
<h2>Skill Gap Intelligence System</h2>

<form method="post">
  <label>Student Name:</label><br>
  <input type="text" name="name" required><br><br>

  <label>Skills Known (comma separated):</label><br>
  <input type="text" name="skills" placeholder="Python, SQL, HTML" required><br><br>

  <label>Career Goal:</label><br>
  <select name="goal" required>
    <option value="" disabled selected>Select your career goal</option>
    {% for goal in career_goals %}
        <option value="{{ goal }}">{{ goal }}</option>
    {% endfor %}
  </select><br><br>

  <button type="submit">Submit</button>
</form>

<br>
<a href="/admin">Go to Admin Page</a>
"""

@app.route("/", methods=["GET", "POST"])
def input_page():
    if request.method == "POST":
        name = request.form["name"]
        skills = [s.strip() for s in request.form["skills"].split(",")]
        goal = request.form["goal"]

        student = {
            "name": name,
            "skills": skills,
            "goal": goal
        }
        students_data.append(student)

        return redirect("/result")

    return render_template_string(INPUT_HTML, career_goals=CAREER_GOALS)

# ------------------ RESULT PAGE ------------------
@app.route("/result")
def result_page():
    if not students_data:
        return redirect("/")

    student = students_data[-1]
    skills = student["skills"]
    goal = student["goal"]

    # Jobs based on skills
    skill_job_map = {
        "Python": ["Backend Developer", "Data Analyst"],
        "SQL": ["Data Engineer", "Database Analyst"],
        "ML": ["Machine Learning Engineer"],
        "AI": ["AI Engineer"],
        "HTML": ["Frontend Developer"],
        "JavaScript": ["Frontend Developer", "Full Stack Developer"]
    }

    jobs_from_skills = set()
    for skill in skills:
        jobs_from_skills.update(skill_job_map.get(skill, []))

    # Career goal → required skills
    goal_skill_map = {
        "AI Engineer": ["Python", "ML", "Deep Learning", "Data Structures"],
        "Data Scientist": ["Python", "Statistics", "ML", "SQL"],
        "Web Developer": ["HTML", "CSS", "JavaScript"],
        "Backend Developer": ["Python", "Flask", "SQL"],
        "Frontend Developer": ["HTML", "CSS", "JavaScript"],
        "Full Stack Developer": ["HTML", "CSS", "JavaScript", "Python", "SQL"]
    }

    required_skills = set(goal_skill_map.get(goal, []))
    missing_skills = required_skills - set(skills)

    # Learning platforms (linked)
    platforms = {
        "Python": "https://www.w3schools.com/python/",
        "ML": "https://www.coursera.org/learn/machine-learning",
        "Deep Learning": "https://www.deeplearning.ai/",
        "SQL": "https://www.w3schools.com/sql/",
        "Data Structures": "https://www.geeksforgeeks.org/data-structures/",
        "Statistics": "https://www.khanacademy.org/math/statistics-probability",
        "Flask": "https://realpython.com/",
        "HTML": "https://www.w3schools.com/html/",
        "CSS": "https://www.w3schools.com/css/",
        "JavaScript": "https://www.w3schools.com/js/"
    }

    html = f"""
    <h2>Skill Gap Analysis Result</h2>

    <p><b>Name:</b> {student['name']}</p>
    <p><b>Career Goal:</b> {goal}</p>
    <p><b>Skills Known:</b> {', '.join(skills)}</p>

    <h3>Jobs Based on Your Current Skills</h3>
    <ul>
        {''.join(f"<li>{job}</li>" for job in jobs_from_skills)}
    </ul>

    <h3>Skills You Need for Your Career Goal</h3>
    <ul>
    """
    if missing_skills:
        for skill in missing_skills:
            link = platforms.get(skill)
            if link:
                html += f"<li>{skill} – <a href='{link}' target='_blank'>Learn Here</a></li>"
            else:
                html += f"<li>{skill}</li>"
    else:
        html += "<li>You already have all skills for this career goal!</li>"

    html += """
    </ul>
    <br>
    <a href="/">Go Back</a> | <a href="/admin">Admin Page</a>
    """
    return html

# ------------------ ADMIN PAGE ------------------
@app.route("/admin")
def admin_page():
    html = "<h2>Admin Dashboard</h2>"

    if not students_data:
        html += "<p>No student data yet.</p>"
    else:
        html += "<ul>"
        for s in students_data:
            html += f"<li><b>{s['name']}</b> | Skills: {', '.join(s['skills'])} | Goal: {s['goal']}</li>"
        html += "</ul>"

    html += "<br><a href='/'>Back to Input</a>"
    return html

# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(debug=True)
