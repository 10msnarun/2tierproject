from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="educentral"
)
cursor = db.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_student", methods=["POST"])
def add_student():
    name = request.form['name']
    cursor.execute("INSERT INTO students (name) VALUES (%s)", (name,))
    db.commit()
    return "Student Added!"

@app.route("/get_students", methods=["GET"])
def get_students():
    cursor.execute("SELECT name FROM students")
    data = cursor.fetchall()
    students = [row[0] for row in data]
    return jsonify(students)

if __name__ == "__main__":
    app.run(debug=True)
