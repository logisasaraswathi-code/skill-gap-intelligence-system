from flask import Flask, request, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("interests.db", check_same_thread=False)

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS student_interest (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            career TEXT,
            skills TEXT,
            timestamp TEXT
        )
    """)
    db.commit()
    db.close()

init_db()

# ---------- SKILLS ----------
CAREER_SKILLS = {
    "AI Engineer": ["python", "machine learning", "deep learning", "sql"],
    "Web Developer": ["html", "css", "javascript", "python", "flask"],
    "Data Analyst": ["python", "statistics", "sql", "excel"]
}

# ---------- STUDENT PAGE ----------
STUDENT_HTML = """
<h2>Skill Gap Intelligence System</h2>
<form method="POST">
    <select name="career" required>
        <option value="">Select Career</option>
        {% for c in careers %}
        <option value="{{c}}">{{c}}</option>
        {% endfor %}
    </select><br><br>

    <input type="text" name="skills" placeholder="python, sql, ml" required><br><br>
    <button type="submit">Analyze</button>
</form>

{% if msg %}
<p style="color:green;">{{msg}}</p>
{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def student():
    msg = ""
    if request.method == "POST":
        career = request.form["career"]
        skills = request.form["skills"]

        db = get_db()
        db.execute(
            "INSERT INTO student_interest (career, skills, timestamp) VALUES (?,?,?)",
            (career, skills, datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        db.commit()
        db.close()

        msg = "Your interest has been recorded successfully ✅"

    return render_template_string(
        STUDENT_HTML,
        careers=CAREER_SKILLS.keys(),
        msg=msg
    )

# ---------- OWNER / ADMIN PAGE ----------
ADMIN_HTML = """
<h2>📊 Owner Dashboard</h2>

<p><b>Total Students:</b> {{total}}</p>

<h3>🔥 Career Interest Count</h3>
<ul>
{% for c in career_data %}
<li>{{c[0]}} → {{c[1]}}</li>
{% endfor %}
</ul>

<h3>🕒 Recent Searches</h3>
<ul>
{% for r in recent %}
<li>{{r[0]}} | {{r[1]}} | {{r[2]}}</li>
{% endfor %}
</ul>
"""

@app.route("/admin")
def admin():
    db = get_db()

    total = db.execute("SELECT COUNT(*) FROM student_interest").fetchone()[0]

    career_data = db.execute("""
        SELECT career, COUNT(*) 
        FROM student_interest 
        GROUP BY career
        ORDER BY COUNT(*) DESC
    """).fetchall()

    recent = db.execute("""
        SELECT career, skills, timestamp 
        FROM student_interest 
        ORDER BY id DESC 
        LIMIT 5
    """).fetchall()

    db.close()

    return render_template_string(
        ADMIN_HTML,
        total=total,
        career_data=career_data,
        recent=recent
    )

# ---------- RUN ----------
if __name__ == "__main__":
    app.run()
