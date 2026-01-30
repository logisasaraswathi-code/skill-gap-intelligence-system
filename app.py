from flask import Flask, request, redirect, session, render_template_string
import sqlite3, hashlib, datetime, json

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("skill_ai.db")
    conn.row_factory = sqlite3.Row
    return conn

db = get_db()
db.executescript("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT,
    department TEXT
);

CREATE TABLE IF NOT EXISTS skills(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    skill TEXT,
    level INTEGER,
    updated_at TEXT
);
""")
db.commit()
db.close()

# ---------------- JOB SKILLS ----------------
JOB_SKILLS = {
    "Data Scientist": ["Python", "Statistics", "Machine Learning", "SQL"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "Flask"],
    "AI Engineer": ["Python", "Deep Learning", "Maths", "TensorFlow"],
    "Cyber Security": ["Networking", "Linux", "Ethical Hacking"]
}

RECOMMEND = {
    "Python": "Python Crash Course (YouTube)",
    "Machine Learning": "Andrew Ng ML Course",
    "Flask": "Flask Mega Tutorial",
    "TensorFlow": "TensorFlow Official Tutorials",
}

# ---------------- HELPERS ----------------
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def login_required():
    return "user" in session

# ---------------- AUTH ----------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        pwd = hash_pass(request.form["password"])

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=? AND password=?", (email,pwd)).fetchone()
        db.close()

        if user:
            session["user"] = dict(user)
            return redirect("/dashboard")

    return render_template_string("""
    <h2>Login</h2>
    <form method="post">
    <input name="email" placeholder="Email"><br>
    <input name="password" type="password" placeholder="Password"><br>
    <button>Login</button>
    </form>
    <a href="/register">Register</a>
    """)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO users(name,email,password,role,department) VALUES(?,?,?,?,?)",
            (request.form["name"],request.form["email"],
             hash_pass(request.form["password"]),
             request.form["role"],request.form["dept"])
        )
        db.commit()
        db.close()
        return redirect("/")
    return render_template_string("""
    <h2>Register</h2>
    <form method="post">
    <input name="name" placeholder="Name"><br>
    <input name="email" placeholder="Email"><br>
    <input name="password" type="password"><br>
    <select name="role">
      <option>User</option>
      <option>Manager</option>
      <option>Admin</option>
    </select><br>
    <input name="dept" placeholder="Department"><br>
    <button>Register</button>
    </form>
    """)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if not login_required(): return redirect("/")

    user = session["user"]
    gap = []
    chart = {}

    if request.method == "POST":
        career = request.form["career"]
        for skill in JOB_SKILLS[career]:
            level = int(request.form.get(skill,0))
            db = get_db()
            db.execute("INSERT INTO skills(user_id,skill,level,updated_at) VALUES(?,?,?,?)",
                (user["id"],skill,level,str(datetime.date.today())))
            db.commit()
            db.close()

    db = get_db()
    user_skills = db.execute("SELECT * FROM skills WHERE user_id=?", (user["id"],)).fetchall()
    db.close()

    skill_levels = {s["skill"]:s["level"] for s in user_skills}
    career = request.args.get("career","Data Scientist")

    for s in JOB_SKILLS[career]:
        lvl = skill_levels.get(s,0)
        if lvl < 3:
            gap.append((s,3-lvl))

    chart = {k:skill_levels.get(k,0) for k in JOB_SKILLS[career]}

    return render_template_string("""
    <h2>Welcome {{u.name}} ({{u.role}})</h2>
    <a href="/logout">Logout</a><hr>

    <form method="post">
    <h3>Select Career</h3>
    <select name="career">
    {% for c in jobs %}<option>{{c}}</option>{% endfor %}
    </select><br><br>

    {% for s in jobs[career] %}
      {{s}}:
      <input type="range" min="0" max="5" name="{{s}}"><br>
    {% endfor %}
    <button>Save Skills</button>
    </form>

    <h3>Skill Gaps</h3>
    {% for g in gap %}
      <p>{{g[0]}} → Learn {{g[1]}} level(s)</p>
      <small>Recommended: {{rec.get(g[0],'General Learning')}}</small>
    {% endfor %}

    <h3>Skill Chart</h3>
    <canvas id="c"></canvas>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
new Chart(document.getElementById("c"),{
 type:'radar',
 data:{
 labels: {{chart.keys()|list}},
 datasets:[{label:'Skill Level',data:{{chart.values()|list}}}]
 }
});
</script>

{% if u.role!="User" %}
<hr><a href="/admin">Admin Panel</a>
{% endif %}
""", u=user, jobs=JOB_SKILLS, gap=gap, chart=chart, career=career, rec=RECOMMEND)

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if not login_required(): return redirect("/")
    if session["user"]["role"]=="User": return "Access Denied"

    db = get_db()
    users = db.execute("SELECT * FROM users").fetchall()
    db.close()

    return render_template_string("""
    <h2>Admin Dashboard</h2>
    <table border=1>
    <tr><th>Name</th><th>Email</th><th>Role</th><th>Dept</th></tr>
    {% for u in users %}
    <tr>
    <td>{{u.name}}</td><td>{{u.email}}</td>
    <td>{{u.role}}</td><td>{{u.department}}</td>
    </tr>
    {% endfor %}
    </table>
    <a href="/dashboard">Back</a>
    """, users=users)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
