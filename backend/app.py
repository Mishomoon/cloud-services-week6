from flask import Flask, jsonify, request
import os
import time
import logging
import mysql.connector
import redis

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

DB_HOST = os.getenv("DB_HOST", "mysql")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "appdb")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True
)


def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


@app.before_request
def start_timer():
    request.start_time = time.time()


@app.after_request
def log_request(response):
    duration = time.time() - request.start_time

    app.logger.info(
        "request path=%s method=%s status=%s response_time_ms=%.2f",
        request.path,
        request.method,
        response.status_code,
        duration * 1000
    )

    return response


@app.route("/api/health")
def health():
    return jsonify(status="ok")


@app.route("/api")
def api():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 'Hello from MySQL via Flask!'")
    message = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return jsonify(message=message)


@app.route("/api/time")
def database_time():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT NOW()")
    current_time = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return jsonify(database_time=str(current_time))


@app.route("/api/visitor")
def visitor_counter():
    visits = redis_client.incr("visitor_count")
    return jsonify(visits=visits)