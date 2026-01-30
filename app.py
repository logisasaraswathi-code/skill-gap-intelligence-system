from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create table if not exists
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interest TEXT,
    likes INTEGER DEFAULT 0
)
""")
conn.commit()
conn.close()

# ---------------- HOME / STUDENT PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        interest = request.form.get("interest")

        if interest:
            conn = get_db()
            conn.execute(
                "INSERT INTO interests (interest) VALUES (?)",
                (interest,)
            )
            conn.commit()
            conn.close()

        return redirect("/")

    conn = get_db()
    data = conn.execute("SELECT * FROM interests").fetchall()
    conn.close()

    return render_template_string("""
        <h2>Skill Gap Intelligence System</h2>

        <form method="post">
            <input type="text" name="interest" placeholder="Enter skill / interest" required>
            <button type="submit">Submit</button>
        </form>

        <h3>Student Interests</h3>
        <ul>
            {% for row in data %}
                <li>
                    {{ row.interest }} —
                    Likes: {{ row.likes }}
                    <a href="/like/{{ row.id }}">👍 Like</a>
                </li>
            {% endfor %}
        </ul>

        <br>
        <a href="/admin">Go to Admin Page</a>
    """, data=data)

# ---------------- LIKE FEATURE ----------------

@app.route("/like/<int:id>")
def like(id):
    conn = get_db()
    conn.execute(
        "UPDATE interests SET likes = likes + 1 WHERE id = ?",
        (id,)
    )
    conn.commit()
    conn.close()
    return redirect("/")

# ---------------- ADMIN PAGE ----------------
@app.route("/admin")
def admin():
    conn = get_db()
    data = conn.execute("SELECT * FROM interests").fetchall()
    conn.close()

    return render_template_string("""
        <h1>Admin Dashboard</h1>

        <table border="1" cellpadding="8">
            <tr>
                <th>ID</th>
                <th>Interest</th>
                <th>Likes</th>
            </tr>
            {% for row in data %}
            <tr>
                <td>{{ row.id }}</td>
                <td>{{ row.interest }}</td>
                <td>{{ row.likes }}</td>
            </tr>
    @app.route("/like/<int:id>")
def like(id):
    conn = get_db()
    conn.execute(
        "UPDATE interests SET likes = likes + 1 WHERE id = ?",
        (id,)
    )
    conn.commit()
    conn.close()
    return redirect("/")        {% endfor %}
        </table>

        <br>
        <a href="/">Back to Student Page</a>
    """, data=data)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
