from flask import Flask, jsonify, render_template_string
import mysql.connector
import os

app = Flask(__name__)

# --- Cloud SQL connection info ---
DB_USER = "root"
DB_PASSWORD = "e2e123!"  # Cloud SQL root password
DB_NAME = "test_db"
# Unix socket path for Cloud SQL connection
DB_SOCKET = "/cloudsql/e2e-test-project-489914:europe-west1:e2e-test-sql"

# --- Home page ---
@app.route("/")
def home():
    html_content = """
    <html>
        <head>
            <title>Cloud SQL SPA Test</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
                #status { margin-top: 20px; font-weight: bold; }
                #last-msg { margin-top: 20px; font-style: italic; }
            </style>
        </head>
        <body>
            <h1>Cloud SQL SPA Test</h1>
            <button onclick="checkDB()">Check Database Connection</button>
            <div id="status"></div>
            <div id="last-msg"></div>

            <script>
                function checkDB() {
                    fetch('/check-db')
                        .then(response => response.json())
                        .then(data => {
                            if(data.status === 'connected') {
                                document.getElementById('status').innerText = "✅ Cloud SQL is connected!";
                                document.getElementById('last-msg').innerText = "Last message: " + data.last_msg;
                            } else {
                                document.getElementById('status').innerText = "❌ Connection failed: " + data.error;
                                document.getElementById('last-msg').innerText = "";
                            }
                        })
                        .catch(err => {
                            document.getElementById('status').innerText = "❌ Error: " + err;
                            document.getElementById('last-msg').innerText = "";
                        });
                }
            </script>
        </body>
    </html>
    """
    return render_template_string(html_content)

# --- Endpoint to check DB ---
@app.route("/check-db")
def check_db():
    try:
        conn = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            unix_socket=DB_SOCKET,
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
        # Insert a new visit message
        cursor.execute("INSERT INTO visits (msg) VALUES ('Hello from Cloud SQL!')")
        conn.commit()
        # Get the last inserted message
        cursor.execute("SELECT msg FROM visits ORDER BY id DESC LIMIT 1")
        last_msg = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return jsonify({"status": "connected", "last_msg": last_msg})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e), "last_msg": ""})

# --- Run locally (optional) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
