from flask import Flask
import mysql.connector
import os

app = Flask(__name__)

# Cloud SQL instance connection name
INSTANCE_CONNECTION_NAME = "e2e-test-project-489914:europe-west1:e2e-test-sql"

# Database credentials
DB_USER = "root"
DB_PASSWORD = "e2e123!"
DB_NAME = "test_db"


@app.route("/check-db")
def check_db():
    try:
        # Connect using Unix socket
        conn = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            unix_socket=f"/cloudsql/{INSTANCE_CONNECTION_NAME}",
            database=DB_NAME
        )

        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                msg VARCHAR(255)
            )
        """)

        # Insert a test message
        cursor.execute("INSERT INTO visits (msg) VALUES ('Hello from Cloud SQL!')")
        conn.commit()

        # Read latest message
        cursor.execute("SELECT msg FROM visits ORDER BY id DESC LIMIT 1")
        message = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return f"✅ Cloud SQL is connected!<br>Latest message: {message}"

    except Exception as e:
        return f"❌ Connection failed: {str(e)}"


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cloud SQL SPA Test</title>
        <style>
            body {
                font-family: Arial;
                text-align: center;
                margin-top: 80px;
                background: #f5f5f5;
            }

            h1 {
                color: #333;
            }

            button {
                padding: 14px 25px;
                font-size: 16px;
                border: none;
                background: #4285F4;
                color: white;
                border-radius: 6px;
                cursor: pointer;
            }

            button:hover {
                background: #2f6fe0;
            }

            #result {
                margin-top: 30px;
                font-size: 18px;
            }
        </style>
    </head>

    <body>

        <h1>Cloud SQL SPA Test</h1>

        <button onclick="checkDB()">
            Check Database Connection
        </button>

        <p id="result"></p>

        <script>
            async function checkDB() {
                const response = await fetch('/check-db');
                const text = await response.text();
                document.getElementById("result").innerHTML = text;
            }
        </script>

    </body>
    </html>
    """


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
