from flask import Flask
import mysql.connector
import os

app = Flask(__name__)

@app.route('/')
def home():
    # Connect to Cloud SQL
    conn = mysql.connector.connect(
        user='root',
        password='E2E123!',
        host='/cloudsql/e2e-test-project-489914:europe-west1:e2e-test-sql',
        database='test_db'  # create this database next
    )
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS visits (id INT AUTO_INCREMENT PRIMARY KEY, msg VARCHAR(255))")
    cursor.execute("INSERT INTO visits (msg) VALUES ('Hello from Cloud SQL!')")
    conn.commit()

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

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
