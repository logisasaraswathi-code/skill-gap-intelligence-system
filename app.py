from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

# ---------- DATABASE ----------
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

# ---------- JOB SKILLS ----------
JOB_SKILLS = {
    "Data Scientist": ["Python", "Statistics", "Machine Learning", "SQL"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "Flask"],
    "AI Engineer": ["Python", "Deep Learning", "TensorFlow", "Maths"],
    "Cyber Security": ["Networking", "Linux", "Ethical Hacking"]
}

# ---------- MAIN PAGE ----------
@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        name = request.form["name"]
        job = request.form["job"]
        skills = [s.strip() for s in request.form["skills"].split(",")]

        required = JOB_SKILLS[job]
        missing = list(set(required) - set(skills))

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
            "missing": missing
        }

    # Fetch all students for admin view
    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Skill Gap Intelligence System</title>
<style>
body{font-family:Arial;background:#f4f6f8;padding:20px}
.card{background:white;max-width:450px;margin:auto;padding:20px;border-radius:10px}
input,select,button{width:100%;padding:10px;margin-top:10px}
button{background:#4CAF50;color:white;border:none}
.skill{background:#eee;padding:8px;margin-top:5px;border-radius:5px}
table{width:100%;border-collapse:collapse;margin-top:30px}
th,td{border:1px solid #ccc;padding:8px}
th{background:#ddd}
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

<button>Submit</button>
</form>

{% if result %}
<hr>
<h3>Hello {{ result.name }}</h3>
<p><b>Career Goal:</b> {{ result.job }}</p>

{% if result.missing %}
<p><b>Skills to Learn:</b></p>
{% for s in result.missing %}
<div class="skill">{{ s }}</div>
{% endfor %}
{% else %}
<p>🎉 All required skills matched!</p>
{% endif %}
{% endif %}
</div>

<!-- ADMIN VIEW -->
<h2 style="margin-top:40px;">Admin View (All Students Data)</h2>
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
""", result=result, students=students)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
