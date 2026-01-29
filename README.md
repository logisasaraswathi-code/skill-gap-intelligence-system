from flask import Flask, request, render_template_string

app = Flask(__name__)

# Skill database
CAREER_SKILLS = {
    "AI Engineer": ["python", "machine learning", "deep learning", "sql"],
    "Web Developer": ["html", "css", "javascript", "python", "flask"],
    "Data Analyst": ["python", "statistics", "sql", "excel"]
}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Skill Gap Intelligence System</title>
    <style>
        body { font-family: Arial; padding: 20px; background:#f4f4f4; }
        input, select, button {
            padding: 10px;
            width: 100%;
            margin: 8px 0;
        }
        .box {
            background: white;
            padding: 15px;
            margin-top: 20px;
            border-radius: 6px;
        }
    </style>
</head>
<body>

<h2>Skill Gap Intelligence System</h2>

<form method="post">
    <input name="name" placeholder="Your Name" required>

    <select name="role">
        {% for role in roles %}
            <option>{{ role }}</option>
        {% endfor %}
    </select>

    <input name="skills" placeholder="Enter skills (comma separated)" required>

    <button type="submit">Analyze</button>
</form>

{% if result %}
<div class="box">
    <p><b>Name:</b> {{ result.name }}</p>
    <p><b>Role:</b> {{ result.role }}</p>
    <p><b>Score:</b> {{ result.score }}%</p>
    <p><b>Matched Skills:</b> {{ result.matched }}</p>
    <p><b>Missing Skills:</b> {{ result.missing }}</p>
    <p><b>Insight:</b> {{ result.insight }}</p>
</div>
{% endif %}

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]
        skills = set(s.strip().lower() for s in request.form["skills"].split(","))

        required = set(CAREER_SKILLS[role])
        matched = skills & required
        missing = required - skills

        score = int(len(matched) / len(required) * 100)

        if score >= 80:
            insight = "High readiness"
        elif score >= 50:
            insight = "Moderate readiness"
        else:
            insight = "Low readiness"

        result = {
            "name": name,
            "role": role,
            "matched": list(matched),
            "missing": list(missing),
            "score": score,
            "insight": insight
        }

    return render_template_string(HTML_PAGE, roles=CAREER_SKILLS.keys(), result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
