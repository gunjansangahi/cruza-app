#version --1.4

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    # No DB validation
    return "Login successful — Welcome to Cruza 🚗"


@app.route("/signup", methods=["POST"])
def signup():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    # No DB insert
    return "Account created successfully!"


@app.route("/dbtest")
def dbtest():
    return "DB connection disabled for testing"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)