from flask import Flask
import mysql.connector

app = Flask(__name__)

@app.route('/')
def home():
    conn = mysql.connector.connect(
        user='root',
        password='E2E123!',
        host='34.140.101.84',  # <-- Public IP of SQL
        port=3306,
        database='test_db'
    )
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS visits (id INT AUTO_INCREMENT PRIMARY KEY, msg VARCHAR(255))")
    cursor.execute("INSERT INTO visits (msg) VALUES ('Hello from Cloud SQL!')")
    conn.commit()

    cursor.execute("SELECT msg FROM visits ORDER BY id DESC LIMIT 1")
    message = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return f"<h1>Database says:</h1><p>{message}</p>"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
