from flask import Flask, request, render_template_string

app = Flask(__name__)

# ---------------- JOB SKILL DATABASE ----------------
JOB_SKILLS = {
    "Data Scientist": ["Python", "Statistics", "Machine Learning", "SQL"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "Flask"],
    "AI Engineer": ["Python", "Deep Learning", "TensorFlow", "Maths"],
    "Cyber Security": ["Networking", "Linux", "Ethical Hacking", "Cryptography"]
}

FREE_PLATFORMS = {
    "Python": "FreeCodeCamp, W3Schools, YouTube",
    "Statistics": "Khan Academy, YouTube",
    "Machine Learning": "Google ML Crash Course, FreeCodeCamp",
    "SQL": "W3Schools, SQLBolt",
    "HTML": "FreeCodeCamp, W3Schools",
    "CSS": "FreeCodeCamp, W3Schools",
    "JavaScript": "FreeCodeCamp, JavaScript.info",
    "Flask": "YouTube, FreeCodeCamp",
    "Deep Learning": "YouTube, Google AI",
    "TensorFlow": "TensorFlow Official Tutorials",
    "Maths": "Khan Academy",
    "Networking": "Cisco Networking Academy",
    "Linux": "Linux Journey, YouTube",
    "Ethical Hacking": "Cybrary, YouTube",
    "Cryptography": "Khan Academy, YouTube"
}

# ---------------- HOME PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        name = request.form["name"]
        job = request.form["job"]
        current_skills = request.form["skills"].split(",")

        current_skills = [skill.strip() for skill in current_skills]
        required_skills = JOB_SKILLS.get(job, [])

        missing_skills = list(set(required_skills) - set(current_skills))

        suggestions = {}
        for skill in missing_skills:
            suggestions[skill] = FREE_PLATFORMS.get(skill, "YouTube")

        result = {
            "name": name,
            "job": job,
            "missing_skills": missing_skills,
            "suggestions": suggestions
        }

    return render_template_string("""
        <h2>Skill Gap Intelligence System</h2>

        <form method="post">
            <input type="text" name="name" placeholder="Student Name" required><br><br>

            <select name="job" required>
                <option value="">Select Job</option>
                <option>Data Scientist</option>
                <option>Web Developer</option>
                <option>AI Engineer</option>
                <option>Cyber Security</option>
            </select><br><br>

            <input type="text" name="skills" placeholder="Your Skills (comma separated)" required><br><br>

            <button type="submit">Check Skill Gap</button>
        </form>

        {% if result %}
            <hr>
            <h3>Hello {{ result.name }} 👋</h3>
            <p><b>Target Job:</b> {{ result.job }}</p>

            {% if result.missing_skills %}
                <h4>Skills You Need to Learn:</h4>
                <ul>
                {% for skill, platform in result.suggestions.items() %}
                    <li><b>{{ skill }}</b> → Learn from: {{ platform }}</li>
                {% endfor %}
                </ul>
            {% else %}
                <p>🎉 You already have all required skills!</p>
            {% endif %}
        {% endif %}
    """ , result=result)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
