from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY_HERE"  # Replace with a strong random key

DATABASE = "skills.db"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """)
        # Skills table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skill_name TEXT,
            progress INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        # Attendance table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        # Notices table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            posted_by TEXT
        )
        """)
        conn.commit()
        conn.close()

init_db()

# ---------------- LOGIN REQUIRED DECORATOR ----------------
from functools import wraps
def login_required(role=None):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                return "Unauthorized", 403
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

# ---------------- ROUTES ----------------
@app.route('/')
def home():
    if 'user_id' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

# ----- LOGIN -----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            flash("Login successful!", "success")
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

# ----- LOGOUT -----
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ----- STUDENT DASHBOARD -----
@app.route('/student')
@login_required(role='student')
def student_dashboard():
    return render_template('student_dashboard.html', name=session['name'])

# ----- ADMIN DASHBOARD -----
@app.route('/admin')
@login_required(role='admin')
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.execute("SELECT * FROM notices")
    notices = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', users=users, notices=notices, name=session['name'])

# ----- ADD NOTICE (ADMIN ONLY) -----
@app.route('/add_notice', methods=['POST'])
@login_required(role='admin')
def add_notice():
    title = request.form['title']
    content = request.form['content']
    posted_by = session['name']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notices (title, content, posted_by) VALUES (?, ?, ?)", (title, content, posted_by))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# ----- VIEW NOTICES (STUDENT) -----
@app.route('/notices')
@login_required(role='student')
def view_notices():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notices")
    notices = cursor.fetchall()
    conn.close()
    return render_template('notices.html', notices=notices)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
