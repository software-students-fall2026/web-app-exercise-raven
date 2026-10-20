from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/class-grades")
def class_grades():
    students = [
        {"name": "Alice", "grade": 92},
        {"name": "Bob", "grade": 85},
        {"name": "Charlie", "grade": 78}
    ]
    return render_template("class_grades.html", students=students)

if __name__ == "__main__":
    app.run(debug=True, port=5001)