from flask import Flask
import mysql.connector
import os

app = Flask(__name__)

# Cloud SQL instance connection name
INSTANCE_CONNECTION_NAME = "e2e-test-project-489914:europe-west1:e2e-test-sql"

Database credentials
DB_USER = "testuser"
DB_PASSWORD = "test123"
DB_NAME = "test_db"


# ✅ NEW ROUTE — GET USERS
@app.route("/users")
def get_users():
    try:
        conn = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            unix_socket=f"/cloudsql/{INSTANCE_CONNECTION_NAME}",
            database=DB_NAME
        )

        cursor = conn.cursor()
        cursor.execute("SELECT name, email FROM users")
        users = cursor.fetchall()

        cursor.close()
        conn.close()

        result = ""
        for user in users:
            result += f"<p><b>{user[0]}</b> - {user[1]}</p>"

        return result

    except Exception as e:
        return f"❌ Error: {str(e)}"


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

        <button onclick="loadUsers()">
            Load Users
        </button>

        <div id="result"></div>

        <script>
            async function loadUsers() {
                const response = await fetch('/users');
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
