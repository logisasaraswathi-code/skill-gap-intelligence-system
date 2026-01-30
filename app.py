from flask import Flask, render_template_string, request

app = Flask(__name__)

CAREER_SKILLS = {
    "Data Scientist": ["Python", "Machine Learning", "SQL"],
    "Web Developer": ["HTML", "CSS", "JavaScript"]
}

FREE_RESOURCES = {
    "Python": "FreeCodeCamp Python, W3Schools",
    "Machine Learning": "Google ML Crash Course, StatQuest",
    "SQL": "SQLBolt, W3Schools SQL",
    "HTML": "MDN HTML",
    "CSS": "CSS Tricks",
    "JavaScript": "JavaScript.info"
}

HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Skill Gap Intelligence System</title>
<style>
body{font-family:Arial;background:#f5f6fa}
.card{max-width:400px;margin:auto;background:white;padding:20px;border-radius:10px}
button{background:green;color:white;padding:10px;border:none;width:100%}
</style>
</head>
<body>
<div class="card">
<h2>Skill Gap Intelligence System</h2>
<form method="POST">
<input name="name" placeholder="Student Name" required><br><br>
<select name="career" required>
<option>Data Scientist</option>
<option>Web Developer</option>
</select><br><br>
<input name="skills" placeholder="Your skills (comma separated)" required><br><br>
<button type="submit">Analyze Skills</button>
</form>
</div>
</body>
</html>
"""

RESULT_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Result</title>
</head>
<body style="font-family:Arial">
<h2>Hello {{name}}</h2>
<h3>Career Goal: {{career}}</h3>

<h3>Skill Analysis</h3>
<ul>
{% for s,p in scores.items() %}
<li>{{s}} : {{p}}%</li>
{% endfor %}
</ul>

<h3>AI Recommendations</h3>
<ul>
{% for r in recs %}
<li>{{r}}</li>
{% endfor %}
</ul>

<a href="/">Go Back</a>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        career = request.form["career"]
        user_skills = [s.strip() for s in request.form["skills"].split(",")]

        required = CAREER_SKILLS[career]
        scores = {}
        recommendations = []

        for skill in required:
            if skill in user_skills:
                scores[skill] = 90
            else:
                scores[skill] = 30
                recommendations.append(f"{skill} → {FREE_RESOURCES[skill]}")

        return render_template_string(
            RESULT_HTML,
            name=name,
            career=career,
            scores=scores,
            recs=recommendations
        )

    return render_template_string(HOME_HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
