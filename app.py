from flask import Flask, request, redirect, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET"

# ---------- DATABASE ----------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///college.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ---------- MODELS ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20))   # student / faculty / admin
    approved = db.Column(db.Boolean, default=False)

class SecretCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True)

# ---------- INIT ----------
@app.before_first_request
def init_db():
    db.create_all()
    if not User.query.filter_by(role="admin").first():
        admin = User(
            email="admin@yourcollege.edu",
            password=generate_password_hash("admin123"),
            role="admin",
            approved=True
        )
        db.session.add(admin)
        db.session.commit()

# ---------- HELPERS ----------
def login_required():
    if "user_id" not in session:
        abort(403)

def admin_only():
    if session.get("role") != "admin":
        abort(403)

# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if not user.approved:
                return "Waiting for admin approval"
            session["user_id"] = user.id
            session["role"] = user.role
            return redirect("/dashboard")
        return "Invalid login"

    return """
<!DOCTYPE html>
<html>
<head>
  <title>College App</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="manifest" href="/static/manifest.json">
</head>
<body>
<h2>College Login</h2>
<form method="post">
Email:<input name="email"><br>
Password:<input type="password" name="password"><br>
<button>Login</button>
</form>
<a href="/register">Register</a>

<script>
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/static/service-worker.js");
}
</script>
</body>
</html>
"""

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        code = request.form["code"]

        if not email.endswith("@yourcollege.edu"):
            return "Only college email allowed"

        if not SecretCode.query.filter_by(code=code).first():
            return "Invalid secret code"

        user = User(
            email=email,
            password=generate_password_hash(password),
            role=role,
            approved=False
        )
        db.session.add(user)
        db.session.commit()
        return "Registered. Wait for admin approval."

    return """
<h2>Register</h2>
<form method="post">
Email:<input name="email"><br>
Password:<input type="password" name="password"><br>
Role:
<select name="role">
<option value="student">Student</option>
<option value="faculty">Faculty</option>
</select><br>
Secret Code:<input name="code"><br>
<button>Register</button>
</form>
"""

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    login_required()
    role = session.get("role")
    admin_link = "<a href='/admin'>Admin Panel</a>" if role == "admin" else ""
    return f"""
<h2>{role.capitalize()} Dashboard</h2>
{admin_link}<br><br>
<a href="/logout">Logout</a>
"""

# ---------- ADMIN ----------
@app.route("/admin")
def admin():
    login_required()
    admin_only()

    users = User.query.filter_by(approved=False).all()
    html = "<h2>Admin Dashboard</h2>"
    html += "<a href='/generate-code'>Generate College Code</a><br><br>"
    for u in users:
        html += f"{u.email} ({u.role}) <a href='/approve/{u.id}'>Approve</a><br>"
    return html

@app.route("/approve/<int:uid>")
def approve(uid):
    login_required()
    admin_only()
    user = User.query.get(uid)
    user.approved = True
    db.session.commit()
    return redirect("/admin")

@app.route("/generate-code")
def generate_code():
    login_required()
    admin_only()
    code = os.urandom(4).hex()
    db.session.add(SecretCode(code=code))
    db.session.commit()
    return f"College Secret Code: {code}"

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- RUN ----------
app.run(host="0.0.0.0", port=3000)
