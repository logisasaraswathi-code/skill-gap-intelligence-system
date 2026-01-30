from flask import Flask, request, redirect, render_template_string
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
    goal TEXT,
    current_skills TEXT,
    required_skills TEXT,
    likes INTEGER DEFAULT 0
)
""")
conn.commit()
conn.close()

# ---------------- STUDENT PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        goal = request.form.get("goal")
        current_skills = request.form.get("current_skills")
        required_skills = request.form.get("required_skills")

        if goal and current_skills and required_skills:
            conn = get_db()
            conn.execute("""
                INSERT INTO skill_gap (goal, current_skills, required_skills)
                VALUES (?, ?, ?)
            """, (goal, current_skills, required_skills))
            conn.commit()
            conn.close()

        return redirect("/")

    conn = get_db()
    data = conn.execute("SELECT * FROM skill_gap").fetchall()
    conn.close()

    return render_template_string("""
        <h2>Skill Gap Intelligence System</h2>

        <form method="post">
            <input type="text" name="goal" placeholder="Career Goal" required><br><br>
            <input type="text" name="current_skills" placeholder="Current Skills" required><br><br>
            <input type="text" name="required_skills" placeholder="Skills Required to Achieve Goal" required><br><br>
            <button type="submit">Submit</button>
        </form>

        <h3>Student Submissions</h3>
        <ul>
            {% for row in data %}
                <li>
                    <b>Goal:</b> {{ row.goal }} <br>
                    <b>Current Skills:</b> {{ row.current_skills }} <br>
                    <b>Required Skills:</b> {{ row.required_skills }} <br>
                    <b>Likes:</b> {{ row.likes }}
                    <a href="/like/{{ row.id }}">👍 Like</a>
                </li>
                <hr>
            {% endfor %}
        </ul>

        <a href="/admin">Go to Admin Dashboard</a>
    """, data=data)

# ---------------- LIKE FEATURE ----------------
@app.route("/like/<int:id>")
def like(id):
    conn = get_db()
    conn.execute(
        "UPDATE skill_gap SET likes = likes + 1 WHERE id = ?",
        (id,)
    )
    conn.commit()
    conn.close()
    return redirect("/")

# ---------------- ADMIN PAGE ----------------
@app.route("/admin")
def admin():
    conn = get_db()
    data = conn.execute("SELECT * FROM skill_gap").fetchall()
    conn.close()

    return render_template_string("""
        <h1>Admin Dashboard – Skill Gap Analysis</h1>

        <table border="1" cellpadding="8">
            <tr>
                <th>ID</th>
                <th>Goal</th>
                <th>Current Skills</th>
                <th>Required Skills</th>
                <th>Likes</th>
            </tr>
            {% for row in data %}
            <tr>
                <td>{{ row.id }}</td>
                <td>{{ row.goal }}</td>
                <td>{{ row.current_skills }}</td>
                <td>{{ row.required_skills }}</td>
                <td>{{ row.likes }}</td>
            </tr>
            {% endfor %}
        </table>

        <br>
        <a href="/">Back to Student Page</a>
    """ , data=data)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
