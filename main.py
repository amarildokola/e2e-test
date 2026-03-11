from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Simple SPA Test</title>
      <style>
        body { font-family: Arial, sans-serif; background: #f4f4f9; margin: 0; padding: 0; text-align: center; }
        header { background: #4a90e2; color: white; padding: 20px; }
        section { margin: 40px auto; max-width: 600px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        p { font-size: 18px; }
      </style>
    </head>
    <body>
      <header>
        <h1>Simple SPA Test</h1>
      </header>
      <section>
        <p id="message">Hello World from E2E test!</p>
        <button onclick="changeMessage()">Click me!</button>
      </section>
      <script>
        function changeMessage() {
          document.getElementById("message").textContent = "You clicked the button! 🎉";
        }
      </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
