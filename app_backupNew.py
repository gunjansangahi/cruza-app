# version --1.4

from flask import Flask, render_template, request
import psycopg2 as p
import boto3
import json
from botocore.exceptions import ClientError


# ---------- GET SECRET FROM AWS ----------
def get_secret():

    secret_name = "cruza_db_connection"
    region_name = "eu-north-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = response['SecretString']

    return json.loads(secret)


# ---------- DATABASE CONNECTION ----------
def get_db_connection():

    secret = get_secret()

    conn = p.connect(
        host = secret["host"],
        database = secret["database"],
        user = secret["username"],
        password = secret["password"],
        port = secret["port"]
    )

    cur = conn.cursor()
    cur.execute("SET search_path TO cruza;")
    cur.close()

    return conn


app = Flask(__name__)


# ---------- DB TEST ----------
@app.route("/dbtest")
def dbtest():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()

        return "Database connected successfully !!!!"

    except Exception as e:
        return str(e)


# ---------- SIGNUP ----------
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


# ---------- LOGIN ----------
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
        return "Login successful — Welcome to Cruza. 🚗"
    else:
        return "Invalid email or password."


# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)