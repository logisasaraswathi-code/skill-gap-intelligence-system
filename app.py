from flask import Flask, request, render_template_string

app = Flask(__name__)

JOB_SKILLS = {
    "Data Scientist": ["Python", "Statistics", "Machine Learning", "SQL"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "Flask"],
    "AI Engineer": ["Python", "Deep Learning", "TensorFlow", "Maths"],
    "Cyber Security": ["Networking", "Linux", "Ethical Hacking"]
}

FREE_PLATFORMS = {
    "Python": "FreeCodeCamp, W3Schools",
    "Statistics": "Khan Academy",
    "Machine Learning": "Google ML Crash Course",
    "SQL": "SQLBolt, W3Schools",
    "HTML": "FreeCodeCamp",
    "CSS": "FreeCodeCamp",
    "JavaScript": "FreeCodeCamp",
    "Flask": "YouTube",
    "Deep Learning": "YouTube",
    "TensorFlow": "TensorFlow Official",
    "Maths": "Khan Academy",
    "Networking": "Cisco Academy",
    "Linux": "Linux Journey",
    "Ethical Hacking": "Cybrary"
}

@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        name = request.form["name"]
        job = request.form["job"]
        skills = request.form["skills"].split(",")

        skills = [s.strip() for s in skills]
        required = JOB_SKILLS[job]
        missing = list(set(required) - set(skills))

        suggestions = {s: FREE_PLATFORMS.get(s, "YouTube") for s in missing}

        result = {
            "name": name,
            "job": job,
            "missing": missing,
            "suggestions": suggestions
        }

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Skill Gap Intelligence System</title>
<style>
body{
    font-family: Arial, sans-serif;
    background: linear-gradient(to right, #667eea, #764ba2);
    padding: 20px;
}
.card{
    background: white;
    max-width: 420px;
    margin: auto;
    padding: 20px;
    border-radius: 12px;
}
h2{
    text-align: center;
    color: #333;
}
input, select, button{
    width: 100%;
    padding: 10px;
    margin-top: 10px;
}
button{
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
}
.result{
    margin-top: 20px;
}
.skill{
    background: #f3f3f3;
    padding: 8px;
    margin-top: 6px;
    border-radius: 6px;
}
</style>
</head>

<body>
<div class="card">
<h2>Skill Gap Intelligence System</h2>

<form method="post">
    <input type="text" name="name" placeholder="Student Name" required>

    <select name="job" required>
        <option value="">Select Career Goal</option>
        <option>Data Scientist</option>
        <option>Web Developer</option>
        <option>AI Engineer</option>
        <option>Cyber Security</option>
    </select>

    <input type="text" name="skills" placeholder="Your Skills (comma separated)" required>

    <button type="submit">Analyze Skills</button>
</form>

{% if result %}
<div class="result">
<hr>
<h3>Hello {{ result.name }} 👋</h3>
<p><b>Career Goal:</b> {{ result.job }}</p>

{% if result.missing %}
<p><b>Skills to Improve:</b></p>
{% for skill, platform in result.suggestions.items() %}
<div class="skill">
<b>{{ skill }}</b><br>
Free Resources: {{ platform }}
</div>
{% endfor %}
{% else %}
<p>🎉 You already meet all required skills!</p>
{% endif %}
</div>
{% endif %}

</div>
</body>
</html>
""", result=result)

if __name__ == "__main__":
    app.run(debug=True)
