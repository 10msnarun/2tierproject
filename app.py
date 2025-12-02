from flask import Flask, render_template, request, jsonify
import mysql.connector
import os
import traceback

app = Flask(__name__)
#my first deploy project
#error3
#my first project
def get_db():
    db_host = os.environ.get("DB_HOST", "localhost")
    db_user = os.environ.get("DB_USER", "root")
    db_password = os.environ.get("DB_PASSWORD", "12345")
    db_name = os.environ.get("DB_NAME", "educentral")
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_student", methods=["POST"])
def add_student():
    name = request.form['name']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name) VALUES (%s)", (name,))
    conn.commit()
    cursor.close()
    conn.close()
    return "Student Added!"

@app.route("/get_students", methods=["GET"])
def get_students():
    print("get_students endpoint was called!")  # Debug marker
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM students")
        data = cursor.fetchall()
        students = [row[0] for row in data]
        cursor.close()
        conn.close()
        print("Fetched students:", students)     # Debug marker
        return jsonify(students)
    except Exception as e:
        print("Error in get_students:", e)
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
