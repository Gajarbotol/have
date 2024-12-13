import os
from flask import Flask, request, jsonify, render_template
import requests
from werkzeug.utils import secure_filename
import threading
import time

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to download the file from the streaming link
def download_file(streaming_link, upload_path):
    response = requests.get(streaming_link, stream=True)
    if response.status_code == 200:
        with open(upload_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):  # Download in chunks
                if chunk:
                    f.write(chunk)
        return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    streaming_link = request.form.get('streaming_link')
    if not streaming_link:
        return jsonify({'error': 'No streaming link provided'}), 400

    filename = secure_filename(streaming_link.split('/')[-1])
    upload_path = f"{app.config['UPLOAD_FOLDER']}/{filename}"

    try:
        if download_file(streaming_link, upload_path):
            return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
        else:
            return jsonify({'error': 'Failed to download file from streaming link'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Auto-ping system removed because Render doesn't need it.

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT environment variable
    app.run(host='0.0.0.0', port=port)
