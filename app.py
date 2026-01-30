from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("skills.db")
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    job TEXT,
    current_skills TEXT,
    missing_skills TEXT
)
""")
conn.commit()
conn.close()

# ---------------- DATA ----------------
JOB_SKILLS = {
    "Data Scientist": ["Python", "Statistics", "Machine Learning", "SQL"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "Flask"],
    "AI Engineer": ["Python", "Deep Learning", "TensorFlow", "Maths"],
    "Cyber Security": ["Networking", "Linux", "Ethical Hacking"]
}

FREE_PLATFORMS = {
    "Python": "FreeCodeCamp",
    "Statistics": "Khan Academy",
    "Machine Learning": "Google ML Crash Course",
    "SQL": "SQLBolt",
    "HTML": "FreeCodeCamp",
    "CSS": "FreeCodeCamp",
    "JavaScript": "FreeCodeCamp",
    "Flask": "YouTube",
    "Deep Learning": "YouTube",
    "TensorFlow": "TensorFlow Official",
    "Maths": "Khan Academy",
    "Networking": "Cisco Academy",
    "Linux": "Linux Journey",
    "Ethical Hacking": "Cybrary"
}

# ---------------- STUDENT PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        name = request.form["name"]
        job = request.form["job"]
        skills = [s.strip() for s in request.form["skills"].split(",")]

        required = JOB_SKILLS[job]
        missing = list(set(required) - set(skills))
        suggestions = {s: FREE_PLATFORMS.get(s, "YouTube") for s in missing}

        conn = get_db()
        conn.execute(
            "INSERT INTO students (name, job, current_skills, missing_skills) VALUES (?, ?, ?, ?)",
            (name, job, ", ".join(skills), ", ".join(missing))
        )
        conn.commit()
        conn.close()

        result = {
            "name": name,
            "job": job,
            "suggestions": suggestions,
            "missing": missing
        }

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Skill Gap Intelligence</title>
<style>
body{font-family:Arial;background:#f0f2f5;padding:20px}
.card{background:white;max-width:420px;margin:auto;padding:20px;border-radius:10px}
input,select,button{width:100%;padding:10px;margin-top:10px}
button{background:#4CAF50;color:white;border:none}
.skill{background:#eee;padding:8px;margin-top:5px;border-radius:5px}
</style>
</head>
<body>
<div class="card">
<h2>Skill Gap Intelligence System</h2>
<form method="post">
<input name="name" placeholder="Student Name" required>
<select name="job" required>
<option value="">Select Career</option>
<option>Data Scientist</option>
<option>Web Developer</option>
<option>AI Engineer</option>
<option>Cyber Security</option>
</select>
<input name="skills" placeholder="Your Skills (comma separated)" required>
<button>Analyze</button>
</form>

{% if result %}
<hr>
<h3>Hello {{ result.name }}</h3>
<p><b>Career:</b> {{ result.job }}</p>

{% if result.missing %}
<p><b>Skills to Learn:</b></p>
{% for s, p in result.suggestions.items() %}
<div class="skill"><b>{{ s }}</b> → {{ p }}</div>
{% endfor %}
{% else %}
<p>🎉 All skills matched!</p>
{% endif %}
{% endif %}
</div>
</body>
</html>
""", result=result)

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin():
    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Admin Dashboard</title>
<style>
body{font-family:Arial;background:#222;color:white;padding:20px}
table{width:100%;border-collapse:collapse}
th,td{border:1px solid #555;padding:10px;text-align:left}
th{background:#444}
</style>
</head>
<body>
<h2>Admin Dashboard</h2>
<table>
<tr>
<th>ID</th>
<th>Name</th>
<th>Career</th>
<th>Current Skills</th>
<th>Missing Skills</th>
</tr>
{% for s in students %}
<tr>
<td>{{ s.id }}</td>
<td>{{ s.name }}</td>
<td>{{ s.job }}</td>
<td>{{ s.current_skills }}</td>
<td>{{ s.missing_skills }}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
""", students=students)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
