from flask import Flask, request, render_template_string

app = Flask(__name__)

# Career skill requirements
CAREER_SKILLS = {
    "AI Engineer": {
        "python": 8,
        "machine learning": 8,
        "deep learning": 7,
        "sql": 6
    },
    "Web Developer": {
        "html": 8,
        "css": 7,
        "javascript": 8,
        "python": 6,
        "flask": 6
    },
    "Data Analyst": {
        "python": 7,
        "statistics": 8,
        "sql": 7,
        "excel": 6
    }
}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Skill Gap Intelligence System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial;
            background: #eef2f7;
            padding: 20px;
        }
        .box {
            max-width: 600px;
            margin: auto;
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        h2 {
            text-align: center;
        }
        input, select, button {
            width: 100%;
            padding: 10px;
            margin: 8px 0;
            border-radius: 6px;
            border: 1px solid #ccc;
        }
        button {
            background: #4f46e5;
            color: white;
            font-size: 16px;
            border: none;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background: #f9fafb;
            border-radius: 8px;
        }
        .low {
            color: red;
        }
        .ok {
            color: green;
        }
    </style>
</head>
<body>

<div class="box">
    <h2>Skill Gap Intelligence System 🚀</h2>

    <form method="POST">
        <label>Select Career</label>
        <select name="career" required>
            <option value="">--Choose--</option>
            {% for career in careers %}
            <option value="{{career}}">{{career}}</option>
            {% endfor %}
        </select>

        <label>Your Skills (0–10)</label>
        <input type="text" name="skills" placeholder="Example: python:6, sql:4, machine learning:5" required>

        <button type="submit">Analyze Skills</button>
    </form>

    {% if result %}
    <div class="result">
        <h3>📊 Analysis Result</h3>
        <p><b>Readiness Score:</b> {{ score }}%</p>

        <h4>Skill Gaps</h4>
        <ul>
            {% for skill, gap in gaps.items() %}
            <li class="low">{{skill}} → Improve by {{gap}}</li>
            {% endfor %}
        </ul>

        <h4>✅ Recommended Focus</h4>
        <ul>
            {% for skill in recommendations %}
            <li class="ok">{{skill}}</li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}
</div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    result = False
    gaps = {}
    recommendations = []
    score = 0

    if request.method == "POST":
        career = request.form["career"]
        user_input = request.form["skills"].lower()

        user_skills = {}
        for item in user_input.split(","):
            skill, level = item.split(":")
            user_skills[skill.strip()] = int(level.strip())

        required_skills = CAREER_SKILLS[career]
        total = len(required_skills)
        matched = 0

        for skill, required_level in required_skills.items():
            user_level = user_skills.get(skill, 0)
            if user_level >= required_level:
                matched += 1
            else:
                gaps[skill] = required_level - user_level
                recommendations.append(f"Learn {skill} to level {required_level}")

        score = int((matched / total) * 100)
        result = True

    return render_template_string(
        HTML_PAGE,
        careers=CAREER_SKILLS.keys(),
        result=result,
        gaps=gaps,
        recommendations=recommendations,
        score=score
    )

if __name__ == "__main__":
    app.run(debug=True)
