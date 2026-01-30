from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create table
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS skill_gap (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    goal TEXT,
    current_skills TEXT,
    required_skills TEXT
)
""")
conn.commit()
conn.close()

# ---------------- STUDENT PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    submitted_data = None

    if request.method == "POST":
        student_name = request.form.get("student_name")
        goal = request.form.get("goal")
        current_skills = request.form.get("current_skills")
        required_skills = request.form.get("required_skills")

        if student_name and goal and current_skills and required_skills:
            conn = get_db()
            conn.execute("""
                INSERT INTO skill_gap
                (student_name, goal, current_skills, required_skills)
                VALUES (?, ?, ?, ?)
            """, (student_name, goal, current_skills, required_skills))
            conn.commit()
            conn.close()

            submitted_data = {
                "student_name": student_name,
                "goal": goal,
                "current_skills": current_skills,
                "required_skills": required_skills
            }

    return render_template_string("""
        <h2>Skill Gap Intelligence System</h2>

        <form method="post">
            <input type="text" name="student_name" placeholder="Student Name" required><br><br>
            <input type="text" name="goal" placeholder="Career Goal" required><br><br>
            <input type="text" name="current_skills" placeholder="Current Skills" required><br><br>
            <input type="text" name="required_skills" placeholder="Skills Required" required><br><br>
            <button type="submit">Submit</button>
        </form>

        {% if submitted_data %}
            <hr>
            <h3>Submitted Details</h3>
            <p><b>Student Name:</b> {{ submitted_data.student_name }}</p>
            <p><b>Career Goal:</b> {{ submitted_data.goal }}</p>
            <p><b>Current Skills:</b> {{ submitted_data.current_skills }}</p>
            <p><b>Skills Required:</b> {{ submitted_data.required_skills }}</p>
        {% endif %}
    """, submitted_data=submitted_data)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
