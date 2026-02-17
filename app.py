from flask import Flask, render_template
import psycopg2 as p
from flask import Flask, render_template, request, redirect

def get_db_connection():
    conn = p.connect(
            host = "cruza-postgress-db.ctko8i0wsxxn.eu-north-1.rds.amazonaws.com",
            database = "cruza_db",
            user = "gunjan",
            password = "Gunjan7827gs",
            port = "5432")
    cur = conn.cursor()
    cur.execute("SET search_path TO cruza;")
    cur.close()
    return conn

app = Flask(__name__)

@app.route("/dbtest")
def dbtest():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return "Database connected successfully!"
    except Exception as e:
        return str(e)

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (name, email, password)
    )

    conn.commit()
    cur.close()
    conn.close()

    return "Account created successfully!"

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE email=%s AND password=%s",
        (email, password)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        return "Login successful — Welcome to Cruza 🚗"
    else:
        return "Invalid email or password"


@app.route("/")
def home():
	return render_template("login.html")

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)
