from flask import Flask
import threading

# Flask app banayein
app = Flask('')

# Home route banayein
@app.route('/')
def home():
    return "Bot is Alive"  # Ye response show hoga jab Flask app ko access kiya jayega

# Function to run the app
def run():
    app.run(host='0.0.0.0', port=8080)  # Flask app ko 0.0.0.0 par 8080 port pe run karayein

# Thread mein Flask app ko run karein
def keep_alive():
    t = threading.Thread(target=run)
    t.start()