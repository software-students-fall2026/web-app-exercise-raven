import os
from dotenv import load_dotenv
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for
from bson.objectid import ObjectId

app = Flask(__name__)
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DBNAME")]


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/students/add", methods = ["GET", "POST"])
def add_student():
    students = list(db.students.find())
    
    if request.method == "GET":
        return render_template("_new_student_form.html", students=students)

    firstName = request.form["ffirstname"]
    prefName = request.form["fprefname"]
    lastName = request.form["flastname"]
    
    student = {
        "first_name": firstName,
        "preferred_name": prefName,
        "last_name": lastName,
    }

    db.students.insert_one(student)

    return redirect(url_for("students"))

@app.route("/students/edit/<student_id>", methods = ["GET", "POST"])
def edit_student(student_id):
    try:
        student_id = ObjectId(student_id)
    except Exception:
        return "Invalid student ID.", 400

    student = db.students.find_one({"_id": student_id})

    if student is None:
        return "Student not found.", 404

    if request.method == "GET":
        return render_template("edit_student.html", student = student)

    firstName = request.form["ffirstname"]
    prefName = request.form["fprefname"]
    lastName = request.form["flastname"]

    db.students.update_one(
        {"_id": student_id},
        {
            "$set": {
            "first_name": firstName,
            "preferred_name": prefName,
            "last_name": lastName,
            }
        },
    )

    return redirect(url_for("students"))

@app.route("/students/delete/<student_id>", methods = ["POST"])
def delete_student(student_id):
    try:
        student_id = ObjectId(student_id)
    except Exception:
        return "Invalid student ID.", 400

    db.students.delete_one({"_id": student_id})
    return redirect(url_for("students"))

@app.route("/students", methods = ["POST", "GET"])
def students():
    students = list(db.students.find().sort("first_name"))
    if request.method == "GET":
        return render_template("students.html", students = students)
    
    query = request.form["searchquery"].strip()
    results = []
    for student in students:
        firstName = student.get("first_name").lower()
        prefName = (student.get("preferred_name")).lower()
        lastName = student.get("last_name").lower()

        if query.lower() in firstName or query.lower() in lastName or query.lower()in prefName:
            results.append(student)

    return render_template("students.html", students = results, query = query)

@app.route("/class-grades")
def class_grades():
    students = list(db.students.find().sort("first_name"))
    #db.assignments.delete_many({})
    #db.students.delete_many({})
    return render_template("class_grades.html", students=students)

@app.route("/class-grades/add", methods=["GET", "POST"])
def add_grade():
    students = list(db.students.find())
    assignments = list(db.assignments.find())

    if request.method == "GET":
        return render_template("add_grade.html", students=students, assignments = assignments)

    student_id = ObjectId(request.form["student_id"])
    assignment_name = request.form["assignment_name"].strip()
    grade = request.form["grade"]
    create = request.form.get("assign-method")
            
    try:
        grade = float(grade)
        if grade < 0 or grade > 100:
            return "Grade must be between 0 and 100.", 400

        if create == "on":
            if not assignment_name:
                return redirect(url_for("class_grades"))
            for assignment in assignments:
                if assignment.get("name").lower() == assignment_name.lower():
                    return redirect(url_for("class_grades"))
            assignment = {
                "name": assignment_name,
                "student_grades": [{"student_id": student_id, "grade": grade}]
            }
            assignment_id = db.assignments.insert_one(assignment).inserted_id
        else:
            assignment_id = ObjectId(request.form["assignment_id"])
            assignment = db.assignments.find_one({"_id": assignment_id})
            student = db.students.find_one({"_id": student_id})
            if db.students.find_one({"_id": student_id, "assignment_grades.assignment_id": assignment_id}):
                edit_grade(student_id)
            else:  
                db.assignments.update_one(
                    {"_id": assignment_id},
                    {"$push": {"student_grades": {"student_id": student_id, "grade": grade}}}
                )

        db.students.update_one(
            {"_id": student_id},
            {"$push": {"assignment_grades": {"assignment_id": assignment_id, "name": assignment.get("name"), "grade": grade}}}
        )
    except (ValueError, TypeError):
        return "Invalid grade or student ID.", 400

    student = db.students.find_one({"_id": student_id})
    all_grades = [g["grade"] for g in student["assignment_grades"]]
    avg = sum(all_grades) / len(all_grades)
    db.students.update_one(
        {"_id": student_id},
        {"$set": {"grade": round(avg, 1)}}
    )
        
    return redirect(url_for("class_grades"))

@app.route("/class-grades/edit/<student_id>", methods=["GET", "POST"])
def edit_grade(student_id):
    try:
        student_id = ObjectId(student_id)
    except Exception:
        return "Invalid student ID.", 400

    student = db.students.find_one({"_id": student_id})

    if student is None:
        return "Student not found.", 404

    if request.method == "GET":
        return render_template("edit_grade.html", student = student)

    try:
        grade = float(request.form["grade"])

        if not 0 <= grade <= 100:
            return "Grade must be between 0 and 100.", 400
    except (ValueError, KeyError):
        return "Invalid grade.", 400

    assignment_id = ObjectId(request.form.get("assignment_id"))
    
    db.students.update_one(
        {
            "_id": student_id, 
            "assignment_grades.assignment_id": assignment_id
        },
        {"$set": {"assignment_grades.$.grade": grade}}
    )

    student = db.students.find_one({"_id": student_id})
    all_grades = [g["grade"] for g in student["assignment_grades"]]
    avg = sum(all_grades) / len(all_grades)

    db.assignments.update_one(
        {
            "_id": assignment_id,
            "student_grades.student_id": student_id
        },
        {"$set": {"student_grades.$.grade": grade}}
    )

    db.students.update_one(
        {"_id": student_id},
        {"$set": {"grade": round(avg, 1)}}
    )

    return redirect(url_for("class_grades"))

@app.route("/class-grades/delete/<student_id>", methods=["POST", "GET"])
def delete_grade(student_id):
    try:
        student_id = ObjectId(student_id)
    except Exception:
        return "Invalid student or assignment ID.", 400

    if request.method == "GET":
        return render_template("delete_grade.html", student = db.students.find_one({"_id": student_id}))

    indiv = request.form.get("delete-method")
    if indiv == "on":
        assignment_id = ObjectId(request.form["assignment_id"])
        assignment = db.assignments.find_one({"_id": assignment_id})
        db.students.update_one(
            {"_id": student_id},
            {
                "$pull": {
                    "assignment_grades": {
                        "assignment_id": assignment_id
                    }
                }
            }
        )

        student = db.students.find_one({"_id": student_id})
        all_grades = [g["grade"] for g in student["assignment_grades"]]
        if len(all_grades) == 0:
            db.students.update_one(
            {"_id": student_id},
            {"$unset": {
                        "grade": "",
                        "assignment_grades": ""
                    }
            }
        )
        else:
            avg = sum(all_grades) / len(all_grades)
            db.students.update_one(
                {"_id": student_id},
                {"$set": {"grade": round(avg, 1)}}
            )

        db.assignments.update_one(
            {
                "_id": assignment_id,
                "student_grades.student_id": student_id
            },
            {"$pull": {"student_grades": {"student_id": student_id}}}
        )

    else:
        db.assignments.update_many(
            {"student_grades.student_id": student_id},
            {"$pull": {"student_grades": {"student_id": student_id}}}
        )

        db.students.update_one(
            {"_id": student_id},
            {"$unset": {
                        "grade": "",
                        "assignment_grades": ""
                    }
            }
        )
    
    return redirect(url_for("class_grades"))


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

# host = '0.0.0.0' added for mobile running
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5001)