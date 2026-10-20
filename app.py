import os
from dotenv import load_dotenv
from pymongo import MongoClient
from flask import Flask, render_template

app = Flask(__name__)
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DBNAME")]


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/class-grades")
def class_grades():
    students = list(db.students.find())

    return render_template("class_grades.html", students=students)


@app.route("/class-overview")
def class_overview():
    students = list(db.students.find())

    grades = [
        student["grade"]
        for student in students
        if isinstance(student.get("grade"), (int, float))
        and not isinstance(student["grade"], bool)
    ]

    total_students = len(students)

    if grades:
        average_grade = sum(grades) / len(grades)
        highest_grade = max(grades)
        lowest_grade = min(grades)
    else:
        average_grade = None
        highest_grade = None
        lowest_grade = None

    return render_template(
        "class_overview.html",
        total_students=total_students,
        average_grade=average_grade,
        highest_grade=highest_grade,
        lowest_grade=lowest_grade
    )

if __name__ == "__main__":
    app.run(debug=True, port=5001)