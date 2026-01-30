# app.py
from flask import Flask, render_template_string, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skillgap.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ======== MODELS ========
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')  # user/admin/manager
    department = db.Column(db.String(50))

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    skill_name = db.Column(db.String(100))
    level = db.Column(db.Integer)  # 1-5

# ======== TEMPLATES ========
base_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }}</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {padding-top: 60px;}
.navbar-brand {font-weight:bold;}
.container {max-width: 500px;}
</style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
  <div class="container-fluid">
    <a class="navbar-brand" href="/">SkillGap</a>
    <div>
    {% if 'user_id' in session %}
      <a class="btn btn-light btn-sm" href="/dashboard">Dashboard</a>
      <a class="btn btn-light btn-sm" href="/logout">Logout</a>
    {% else %}
      <a class="btn btn-light btn-sm" href="/login">Login</a>
      <a class="btn btn-light btn-sm" href="/register">Register</a>
    {% endif %}
    </div>
  </div>
</nav>
<div class="container">
{% block content %}{% endblock %}
</div>
</body>
</html>
"""

# Login page
login_html = """
{% extends "base" %}
{% block content %}
<h2>Login</h2>
<form method="POST">
  <input class="form-control mb-2" type="email" name="email" placeholder="Email" required>
  <input class="form-control mb-2" type="password" name="password" placeholder="Password" required>
  <button class="btn btn-primary w-100" type="submit">Login</button>
</form>
<p class="mt-2">Don't have an account? <a href="/register">Register</a></p>
{% endblock %}
"""

# Register page
register_html = """
{% extends "base" %}
{% block content %}
<h2>Register</h2>
<form method="POST">
  <input class="form-control mb-2" type="text" name="name" placeholder="Full Name" required>
  <input class="form-control mb-2" type="email" name="email" placeholder="Email" required>
  <input class="form-control mb-2" type="password" name="password" placeholder="Password" required>
  <input class="form-control mb-2" type="text" name="department" placeholder="Department">
  <button class="btn btn-success w-100" type="submit">Register</button>
</form>
<p class="mt-2">Already have an account? <a href="/login">Login</a></p>
{% endblock %}
"""

# Dashboard page
dashboard_html = """
{% extends "base" %}
{% block content %}
<h2>Dashboard</h2>
<p>Welcome, {{ user.name }}! Role: {{ user.role }}</p>

<h4>Your Skills</h4>
<form method="POST" action="/add_skill">
  <input class="form-control mb-1" type="text" name="skill_name" placeholder="Skill name" required>
  <input class="form-control mb-1" type="number" name="level" placeholder="Skill level 1-5" min="1" max="5" required>
  <button class="btn btn-primary w-100 mb-3" type="submit">Add Skill</button>
</form>

<ul class="list-group mb-3">
{% for s in skills %}
<li class="list-group-item">{{ s.skill_name }} - Level {{ s.level }}</li>
{% else %}
<li class="list-group-item">No skills added yet.</li>
{% endfor %}
</ul>

<h4>Skill Distribution Chart</h4>
<canvas id="skillChart"></canvas>
<script>
const ctx = document.getElementById('skillChart');
const skillChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: {{ skill_names | safe }},
        datasets: [{
            label: 'Skill Level',
            data: {{ skill_levels | safe }},
            backgroundColor: 'rgba(54, 162, 235, 0.7)'
        }]
    },
    options: {
        scales: { y: { beginAtZero: true, max:5 } }
    }
});
</script>
{% endblock %}
"""

# ======== ROUTES ========
@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        name = request.form['name']
        dept = request.form.get('department')
        if User.query.filter_by(email=email).first():
            return "Email already exists"
        user = User(email=email, password=password, name=name, department=dept)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template_string(register_html, title="Register", session=session)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect('/dashboard')
        return "Invalid credentials"
    return render_template_string(login_html, title="Login", session=session)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    skills = Skill.query.filter_by(user_id=user.id).all()
    skill_names = [s.skill_name for s in skills]
    skill_levels = [s.level for s in skills]
    return render_template_string(dashboard_html, user=user, skills=skills,
                                  skill_names=skill_names, skill_levels=skill_levels,
                                  title="Dashboard", session=session)

@app.route('/add_skill', methods=['POST'])
def add_skill():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    name = request.form['skill_name']
    level = int(request.form['level'])
    skill = Skill(user_id=user_id, skill_name=name, level=level)
    db.session.add(skill)
    db.session.commit()
    return redirect('/dashboard')

# ======== INIT DB ========
if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
