import os
import pymysql
from flask import Flask

app = Flask(__name__)

# 🔧 Database configuration from environment variables
DB_USER = os.environ.get("DB_USER", "appuser")
DB_PASS = os.environ.get("DB_PASS", "mysecretpassword")
DB_NAME = os.environ.get("DB_NAME", "sampledb")
DB_CONNECTION_NAME = os.environ.get("DB_CONNECTION_NAME", "root-amulet-454410-j9:us-central1:my-sql-instanc")

# 🔗 Create a database connection
def get_connection():
    try:
        connection = pymysql.connect(
            user=DB_USER,
            password=DB_PASS,
            unix_socket=f"/cloudsql/{DB_CONNECTION_NAME}",
            db=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        return None

@app.route('/')
def index():
    conn = get_connection()
    if not conn:
        return "❌ Failed to connect to Cloud SQL. Check connection details in app.yaml."
    with conn.cursor() as cursor:
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
    return f"✅ Connected to Cloud SQL!<br>Server time: {result['NOW()']}"

@app.route('/insert')
def insert_sample():
    conn = get_connection()
    if not conn:
        return "❌ Database connection failed!"
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                text VARCHAR(255)
            );
        """)
        cursor.execute("INSERT INTO messages (text) VALUES ('Hello from App Engine!');")
        conn.commit()
    return "✅ Inserted sample record successfully."

@app.route('/list')
def list_messages():
    conn = get_connection()
    if not conn:
        return "❌ Database connection failed!"
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM messages;")
        rows = cursor.fetchall()
    if not rows:
        return "No messages found yet."
    return "<br>".join([f"{row['id']}: {row['text']}" for row in rows])

if __name__ == "__main__":
    # Runs locally or in App Engine
    app.run(host="0.0.0.0", port=8080, debug=True)
