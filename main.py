from flask import Flask
import mysql.connector
import os

app = Flask(__name__)

# Cloud SQL connection info
DB_USER = "root"
DB_PASSWORD = "e2e123!"
DB_NAME = "test_db"
DB_HOST = "34.140.101.84"  # Cloud SQL public IP
DB_PORT = 3306

@app.route("/")
def home():
    try:
        # Connect to Cloud SQL
        conn = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = conn.cursor()
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                msg VARCHAR(255)
            )
        """)
        # Insert a new visit message
        cursor.execute("INSERT INTO visits (msg) VALUES ('Hello from Cloud SQL!')")
        conn.commit()
        # Get last message
        cursor.execute("SELECT msg FROM visits ORDER BY id DESC LIMIT 1")
        message = cursor.fetchone()[0]

        cursor.close()
        conn.close()
        return f"""
        <html>
            <body>
                <h1>Database says:</h1>
                <p>{message}</p>
            </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Error connecting to database:</h1><p>{e}</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
