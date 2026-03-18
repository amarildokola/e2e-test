from flask import Flask, Response
import mysql.connector
from google.cloud import storage
import mimetypes
import os

app = Flask(__name__)

# Cloud SQL instance connection name
# INSTANCE_CONNECTION_NAME = "e2e-test-project-489914:europe-west1:e2e-test-sql"

# Database credentials
DB_USER = "testuser"
DB_PASSWORD = "test123"
DB_NAME = "test_db"

# Bucket name
BUCKET_NAME = "e2e-test-bucket-amarildo"


# ✅ NEW ROUTE — SERVE IMAGES FROM BUCKET
@app.route("/image/<filename>")
def get_image(filename):
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)

        image_bytes = blob.download_as_bytes()

        # detect correct file type
        mime_type, _ = mimetypes.guess_type(filename)

        return Response(image_bytes, mimetype=mime_type or 'application/octet-stream')

    except Exception as e:
        return f"Error loading image: {str(e)}"


# ✅ UPDATED ROUTE — GET USERS WITH IMAGES
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
        cursor.execute("SELECT name, email, image FROM users")
        users = cursor.fetchall()

        cursor.close()
        conn.close()

        result = ""

        for user in users:
            name = user[0]
            email = user[1]
            image = user[2]

            # IMPORTANT: now using backend route, not public URL
            image_url = f"/image/{image}"

            result += f"""
            <div class="card">
                <img src="{image_url}">
                <div class="name">{name}</div>
                <div class="email">{email}</div>
            </div>
            """ 

        return result

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ✅ FRONTEND
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Users with Images</title>
        <style>
            body {
                font-family: Arial;
                background: #f5f5f5;
                text-align: center;
                margin: 0;
                padding: 0;
            }

            h1 {
                margin-top: 40px;
                color: #333;
            }

            button {
                margin-top: 20px;
                padding: 12px 25px;
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
                display: flex;
                justify-content: center;
                gap: 30px;
                margin-top: 40px;
                flex-wrap: wrap;
            }

            .card {
                background: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                width: 180px;
            }

            .card img {
                width: 120px;
                height: 120px;
                object-fit: cover;
                border-radius: 50%;
                margin-bottom: 10px;
            }

            .name {
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 5px;
            }

            .email {
                font-size: 14px;
                color: #666;
            }
        </style>
    </head>

    <body>

        <h1>Users</h1>

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
