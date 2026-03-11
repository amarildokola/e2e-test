from flask import Flask
import os
from google.cloud.sql.connector import Connector
import pymysql

app = Flask(__name__)
connector = Connector()

INSTANCE_CONNECTION_NAME = "e2e-test-project-489914:europe-west1:e2e-test-sql"

def getconn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pymysql",
        user="root",
        password="E2E123!",
        db="test_db"
    )
    return conn

@app.route('/')
def home():
    conn = getconn()
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
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
