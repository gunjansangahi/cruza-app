# version --1.5

from flask import Flask, render_template, request
import psycopg2 as p
import boto3
import json
from botocore.exceptions import ClientError
import os
import logging
import uuid
from datetime import datetime


# ---------- DYNAMODB LOGGER SETUP ----------

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
log_table = dynamodb.Table('cruza_app_log')


class DynamoDBHandler(logging.Handler):

    def emit(self, record):

        try:

            log_entry = self.format(record)

            log_table.put_item(
                Item={
                    "log_id": str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "message": log_entry,
                    "module": record.module
                }
            )

        except Exception as e:
            print("DynamoDB logging failed:", e)


logger = logging.getLogger("cruza_logger")
logger.setLevel(logging.INFO)

dynamo_handler = DynamoDBHandler()

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)

dynamo_handler.setFormatter(formatter)

logger.addHandler(dynamo_handler)


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

        logger.info("Fetching database secret")

        response = client.get_secret_value(
            SecretId=secret_name
        )

    except ClientError as e:

        logger.error(f"Secret Manager error: {str(e)}")

        raise e

    secret = response['SecretString']

    return json.loads(secret)


# ---------- DATABASE CONNECTION ----------
def get_db_connection():

    try:

        logger.info("Creating database connection")

        secret = get_secret()

        conn = p.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            port=os.environ['DB_PORT']
        )

        cur = conn.cursor()
        cur.execute("SET search_path TO cruza;")
        cur.close()

        logger.info("Database connection successful")

        return conn

    except Exception as e:

        logger.error(f"Database connection failed: {str(e)}")

        raise


app = Flask(__name__)


# ---------- DB TEST ----------
@app.route("/dbtest")
def dbtest():

    try:

        logger.info("DB test endpoint called")

        conn = get_db_connection()

        cur = conn.cursor()
        cur.execute("SELECT 1;")

        cur.close()
        conn.close()

        logger.info("DB test successful")

        return "Database connected successfully !!!!"

    except Exception as e:

        logger.error(f"DB test failed: {str(e)}")

        return str(e)


# ---------- SIGNUP ----------
@app.route("/signup", methods=["POST"])
def signup():

    try:

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        logger.info(f"Signup attempt: {email}")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )

        conn.commit()

        cur.close()
        conn.close()

        logger.info(f"User signup successful: {email}")

        return "Account created successfully!"

    except Exception as e:

        logger.error(f"Signup failed for {email}: {str(e)}")

        return "Signup failed"


# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():

    try:

        email = request.form["email"]
        password = request.form["password"]

        logger.info(f"Login attempt: {email}")

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

            logger.info(f"Login successful: {email}")

            return "Login successful — Welcome to Cruza. 🚗"

        else:

            logger.warning(f"Invalid login attempt: {email}")

            return "Invalid email or password."

    except Exception as e:

        logger.error(f"Login error for {email}: {str(e)}")

        return "Login failed"


# ---------- HOME ----------
@app.route("/")
def home():

    logger.info("Home page accessed")

    return render_template("login.html")


if __name__ == "__main__":

    logger.info("Cruza application started")

    app.run(host="0.0.0.0", port=5000)