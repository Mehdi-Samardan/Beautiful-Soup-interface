# app.py
from flask import Flask, render_template, request, redirect, url_for, send_file
import uuid
import os
from utils import process_url, send_all_properties

app = Flask(__name__)

# Dictionary to temporarily store processed results
RESULTS = {}

# Update this webhook URL as needed
WEBHOOK_URL = "https://hook.eu2.make.com/is1dhkyhge8iuqg4jsxykh6dkyaejawy"

# Home page: URL submission form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url_input = request.form.get("url")
        if not url_input:
            error = "Please enter a valid URL."
            return render_template("index.html", error=error)
        
        headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/87.0.4280.66 Safari/537.36")
        }
        
        # Process the URL
        result = process_url(url_input, headers)
        if not result:
            error = "An error occurred while processing the URL."
            return render_template("index.html", error=error)
        
        # Generate a unique process ID and store the result
        process_id = str(uuid.uuid4())
        RESULTS[process_id] = result
        
        # Render the result page with the process ID
        return render_template("result.html", result=result, process_id=process_id)
    
    return render_template("index.html")

# Endpoint to send data to the webhook
@app.route("/send_webhook/<process_id>", methods=["POST"])
def send_webhook(process_id):
    result = RESULTS.get(process_id)
    if not result:
        return "Process not found.", 404
    
    send_all_properties(result, WEBHOOK_URL)
    
    # Optionally remove the result from storage after sending
    del RESULTS[process_id]
    
    return render_template("webhook_sent.html", process_id=process_id)

# Endpoint to download the images ZIP file
@app.route("/download_zip")
def download_zip():
    file_path = request.args.get("file")
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found.", 404

if __name__ == "__main__":
    app.run(debug=True)
