from flask import Flask, render_template, request, redirect, url_for, send_file, Response
import uuid
import os
import json
from utils import process_url, send_all_properties

app = Flask(__name__)

# İşlenmiş sonuçları geçici saklamak için sözlük
RESULTS = {}

# Webhook URL – ihtiyaca göre güncelleyin.
WEBHOOK_URL = "https://hook.eu2.make.com/is1dhkyhge8iuqg4jsxykh6dkyaejawy"

# Ana sayfa: URL girişi ve içerik modunun seçimi.
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url_input = request.form.get("url")
        content_mode = request.form.get("content_mode", "clean")  # Varsayılan "clean"
        if not url_input:
            error = "Please enter a valid URL."
            return render_template("index.html", error=error)
        
        headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/87.0.4280.66 Safari/537.36")
        }
        
        result = process_url(url_input, headers, content_mode=content_mode)
        if not result:
            error = "An error occurred while processing the URL."
            return render_template("index.html", error=error)
        
        process_id = str(uuid.uuid4())
        RESULTS[process_id] = result
        
        return render_template("result.html", result=result, process_id=process_id)
    
    return render_template("index.html")

# Webhook'a veri gönderme endpoint'i.
@app.route("/send_webhook/<process_id>", methods=["POST"])
def send_webhook(process_id):
    result = RESULTS.get(process_id)
    if not result:
        return "Process not found.", 404
    
    send_all_properties(result, WEBHOOK_URL)
    del RESULTS[process_id]
    
    return render_template("webhook_sent.html", process_id=process_id)

# Görsellerin ZIP dosyasını indirme endpoint'i.
@app.route("/download_zip")
def download_zip():
    file_path = request.args.get("file")
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found.", 404

# İşlenmiş sonuç JSON dosyasını indirme endpoint'i.
@app.route("/download_json/<process_id>")
def download_json(process_id):
    result = RESULTS.get(process_id)
    if not result:
        return "Process not found.", 404
    json_str = json.dumps(result, indent=4)
    return Response(json_str, mimetype="application/json",
                    headers={"Content-Disposition": f"attachment;filename=result_{process_id}.json"})

if __name__ == "__main__":
    app.run(debug=True)
