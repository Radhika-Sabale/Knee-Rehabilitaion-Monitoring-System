from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from exercise_selector import get_exercise
from progress_graph import generate_graph
import subprocess
import sys
import csv
import os

app = Flask(__name__)
CORS(app)
app.secret_key = "rehabcare_secret"

USERS_FILE = "users.csv"

def get_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users[row['email']] = row['password']
    return users

def save_user(email, password):
    file_exists = os.path.exists(USERS_FILE)
    with open(USERS_FILE, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['email', 'password'])
        if not file_exists:
            writer.writeheader()
        writer.writerow({'email': email, 'password': password})

@app.route("/")
def home():
    return send_from_directory("templates", "index.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password required"})
    users = get_users()
    if email in users:
        return jsonify({"status": "error", "message": "Email already registered"})
    save_user(email, password)
    return jsonify({"status": "success", "message": "Registration successful"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    users = get_users()
    if email not in users:
        return jsonify({"status": "error", "message": "Email not found"})
    if users[email] != password:
        return jsonify({"status": "error", "message": "Incorrect password"})
    session['email'] = email
    return jsonify({"status": "success", "email": email})

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('email', None)
    return jsonify({"status": "success"})

@app.route("/select_exercise", methods=["POST"])
def select_exercise():
    data = request.json
    choice = data.get("choice")
    email = data.get("email")

    exercise = get_exercise(choice)
    print("Selected Exercise:", exercise)

    # Walking launches its own script
    if exercise == "walking":
        subprocess.Popen([sys.executable, "walking_progress_tracker.py", choice, email])
    else:
        subprocess.Popen([sys.executable, "main.py", choice, email])

    return jsonify({"status": "success", "exercise": exercise})

@app.route("/progress/<exercise_type>/<path:email>")
def progress(exercise_type, email):
    img_path = generate_graph(exercise_type, email)
    if img_path is None:
        return "No data available for this exercise.", 404
    return send_from_directory(
        "static",
        f"progress_{exercise_type}_{email.replace('@','_').replace('.','_')}.png"
    )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)