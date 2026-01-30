from flask import Flask, request, render_template_string
import sqlite3
import os

app = Flask(__name__)

# ---------------- DATABASE ----------------
DB_NAME = "skills.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        career TEXT,
        current_skills TEXT,
        missing_skills TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- JOB SKILLS ----------------
JOB_SKILLS = {
    "Data Scientist": ["Python", "Statistics", "Machine Learning", "SQL"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "Flask"],
    "AI Engineer": ["Python", "Deep Learning", "TensorFlow", "Maths"],
    "Cyber Security": ["Networking", "Linux", "Ethical Hacking"]
}

# ---------------- HOME (USER PAGE) ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        name = request.form["name"]
        career = request.form["career"]
        skills = [s.strip().lower() for s in request.form["skills"].split(",")]

        required = [r.lower() for r in JOB_SKILLS[career]]
        missing = list(set(required) - set(skills))

        conn = get_db()
        conn.execute(
            "INSERT INTO students (name, career, current_skills, missing_skills) VALUES (?, ?, ?, ?)",
            (
                name,
                career,
                ", ".join(skills),
                ", ".join(missing)
            )
        )
        conn.commit()
        conn.close()

        result = {
            "name": name,
            "career": career,
            "missing": missing
        }

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Skill Gap Intelligence System</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial;background:#f2f4f7;padding:20px}
.card{background:#fff;max-width:420px;margin:auto;padding:20px;border-radius:12px;box-shadow:0 0 10px #ccc}
input,select,button{width:100%;padding:12px;margin-top:10px;border-radius:6px;border:1px solid #ccc}
button{background:#4CAF50;color:white;border:none;font-size:16px}
.skill{background:#eee;padding:8px;margin-top:6px;border-radius:5px}
a{display:block;text-align:center;margin-top:15px}
</style>
</head>

<body>

<div class="card">
<h2>Skill Gap Intelligence System</h2>

<form method="post">
<input name="name" placeholder="Student Name" required>

<select name="career" required>
<option value="">Select Career</option>
{% for c in jobs %}
<option>{{ c }}</option>
{% endfor %}
</select>

<input name="skills" placeholder="Your Skills (comma separated)" required>

<button>Analyze Skills</button>
</form>

{% if result %}
<hr>
<h3>Hello {{ result.name }}</h3>
<p><b>Career:</b> {{ result.career }}</p>

{% if result.missing %}
<p><b>Skills to Learn:</b></p>
{% for s in result.missing %}
<div class="skill">{{ s }}</div>
{% endfor %}
{% else %}
<p>🎉 All required skills matched!</p>
{% endif %}
{% endif %}

<a href="/admin">Go to Admin Dashboard</a>
</div>

</body>
</html>
""", result=result, jobs=JOB_SKILLS)

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
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial;background:#f4f6f8;padding:20px}
table{width:100%;border-collapse:collapse;background:white}
th,td{border:1px solid #ccc;padding:8px;text-align:left}
th{background:#ddd}
h2{text-align:center}
</style>
</head>

<body>
<h2>Admin Dashboard – All Students Data</h2>

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
<td>{{ s.career }}</td>
<td>{{ s.current_skills }}</td>
<td>{{ s.missing_skills }}</td>
</tr>
{% endfor %}
</table>

<p style="text-align:center;margin-top:20px;">
<a href="/">← Back to User Page</a>
</p>
</body>
</html>
""", students=students)

# ---------------- RUN (RENDER SAFE) ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
