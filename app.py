from flask import Flask, request, render_template_string

app = Flask(__name__)

# Skill database
CAREER_SKILLS = {
    "AI Engineer": ["python", "machine learning", "deep learning", "sql"],
    "Web Developer": ["html", "css", "javascript", "python", "flask"],
    "Data Analyst": ["python", "statistics", "sql", "excel"]
}

# HTML Template
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Skill Gap Intelligence System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial;
            background: #f4f6f8;
            padding: 20px;
        }
        .box {
            max-width: 500px;
            margin: auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
        }
        input, select, button {
            width: 100%;
            padding: 10px;
            margin: 8px 0;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
        }
        ul {
            padding-left: 20px;
        }
    </style>
</head>
<body>
    <div class="box">
        <h2>Skill Gap Intelligence System</h2>
        <form method="post">
            <label>Select Career</label>
            <select name="career" required>
                <option value="AI Engineer">AI Engineer</option>
                <option value="Web Developer">Web Developer</option>
                <option value="Data Analyst">Data Analyst</option>
            </select>

            <label>Your Skills (comma separated)</label>
            <input type="text" name="skills" placeholder="python, sql" required>

            <button type="submit">Analyze Skill Gap</button>
        </form>

        {% if gap is not none %}
            <h3>Missing Skills:</h3>
            {% if gap %}
                <ul>
                {% for skill in gap %}
                    <li>{{ skill }}</li>
                {% endfor %}
                </ul>
            {% else %}
                <p>🎉 You have all required skills!</p>
            {% endif %}
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    gap = None
    if request.method == "POST":
        career = request.form.get("career")
        user_skills = request.form.get("skills", "").lower().replace(" ", "").split(",")
        required_skills = [s.lower() for s in CAREER_SKILLS.get(career, [])]
        gap = [s for s in required_skills if s not in user_skills]

    return render_template_string(HTML_PAGE, gap=gap)

if __name__ == "__main__":
    app.run()
