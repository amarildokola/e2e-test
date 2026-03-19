from flask import Flask, Response
import mysql.connector
from google.cloud import storage
import mimetypes
import os
import requests

# Create Flask app
app = Flask(__name__)

# Cloud SQL connection (used via Unix socket in Cloud Run)
INSTANCE_CONNECTION_NAME = "e2e-test-project-489914:europe-west1:e2e-test-sql"

# Database credentials
DB_USER = "testuser"
DB_PASSWORD = "test123"
DB_NAME = "test_db"

# Cloud Storage bucket name (stores images)
BUCKET_NAME = "e2e-test-bucket-amarildo"


# ROUTE: Serve images from Cloud Storage (via backend)
@app.route("/image/<filename>")
def get_image(filename):
    try:
        # Connect to Cloud Storage
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)

        # Download image as bytes
        image_bytes = blob.download_as_bytes()

        # Detect correct MIME type (jpg, png, etc.)
        mime_type, _ = mimetypes.guess_type(filename)

        # Return image to browser
        return Response(image_bytes, mimetype=mime_type or 'application/octet-stream')

    except Exception as e:
        return f"Error loading image: {str(e)}"


# ROUTE: Get users from Cloud SQL and display them
@app.route("/users")
def get_users():
    try:
        # Connect to Cloud SQL using Unix socket
        conn = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            unix_socket=f"/cloudsql/{INSTANCE_CONNECTION_NAME}",
            database=DB_NAME
        )

        cursor = conn.cursor()

        # Fetch users from database
        cursor.execute("SELECT name, email, image FROM users")
        users = cursor.fetchall()

        cursor.close()
        conn.close()

        result = ""

        # Loop through users and build HTML cards
        for user in users:
            name = user[0]
            email = user[1]
            image = user[2]

            # Use backend route to serve image (not public URL)
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


# ROUTE: Call VM to analyze users (Cloud Run → VM)
@app.route("/analyze-vm")
def analyze_vm():
    try:
        # Send request to VM external IP
        response = requests.get("http://34.14.85.38:5000/analyze")

        # Return VM response to frontend
        return response.text

    except Exception as e:
        return f"❌ VM Error: {str(e)}"


# FRONTEND (Single Page App)
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

            /* Container for user cards */
            #result {
                display: flex;
                justify-content: center;
                gap: 30px;
                margin-top: 40px;
                flex-wrap: wrap;
            }

            /* User card styling */
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

        <!-- Button to load users from DB -->
        <button onclick="loadUsers()">
            Load Users
        </button>

        <!-- Button to trigger VM analysis -->
        <button onclick="analyzeVM()">
            Analyze Users (VM)
        </button>               

        <!-- Where results are displayed -->
        <div id="result"></div>

        <script>
            // Calls /users endpoint and displays result
            async function loadUsers() {
                const response = await fetch('/users');
                const text = await response.text();
                document.getElementById("result").innerHTML = text;
            }
        </script>

        <script>
            // Calls VM through backend and displays result
            async function analyzeVM() {
                const response = await fetch('/analyze-vm');
                const text = await response.text();
                document.getElementById("result").innerHTML = text;
            }
        </script>

    </body>
    </html>
    """


# Run app (Cloud Run uses PORT env variable)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
