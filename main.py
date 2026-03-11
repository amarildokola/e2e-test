from flask import Flask, jsonify, render_template_string
import mysql.connector

app = Flask(__name__)

DB_USER = "root"
DB_PASSWORD = "e2e123!"  # Cloud SQL passwor
DB_NAME = "test_db"
DB_HOST = "34.140.101.84"  # Cloud SQL public IP
DB_PORT = 3306

# Home page
@app.route("/")
def home():
    # Inline HTML with button & JS
    html_content = """
    <html>
        <head>
            <title>Cloud SQL Test</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
                #status { margin-top: 20px; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>Cloud SQL Connection Test</h1>
            <button onclick="checkDB()">Check Database Connection</button>
            <div id="status"></div>

            <script>
                function checkDB() {
                    fetch('/check-db')
                        .then(response => response.json())
                        .then(data => {
                            if(data.status === 'connected') {
                                document.getElementById('status').innerText = "✅ Cloud SQL is connected!";
                            } else {
                                document.getElementById('status').innerText = "❌ Connection failed: " + data.error;
                            }
                        })
                        .catch(err => {
                            document.getElementById('status').innerText = "❌ Error: " + err;
                        });
                }
            </script>
        </body>
    </html>
    """
    return render_template_string(html_content)

# Endpoint to check DB connection
@app.route("/check-db")
def check_db():
    try:
        conn = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  # simple query to test connection
        cursor.close()
        conn.close()
        return jsonify({"status": "connected"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
