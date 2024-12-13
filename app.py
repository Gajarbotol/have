from flask import Flask, request, jsonify, render_template
import requests
from werkzeug.utils import secure_filename
import threading
import time

app = Flask(__name__)

# Upload directory
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
    return render_template('index.html')  # Renders the HTML interface

@app.route('/upload', methods=['POST'])
def upload():
    streaming_link = request.form.get('streaming_link')  # Get the streaming link from the form
    if not streaming_link:
        return jsonify({'error': 'No streaming link provided'}), 400

    # Define the filename and upload path
    filename = secure_filename(streaming_link.split('/')[-1])
    upload_path = f"{app.config['UPLOAD_FOLDER']}/{filename}"

    try:
        # Download the file
        if download_file(streaming_link, upload_path):
            return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
        else:
            return jsonify({'error': 'Failed to download file from streaming link'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ping system to keep the app alive
def auto_ping():
    while True:
        try:
            requests.get('http://127.0.0.1:5000')  # Ping the app locally
        except Exception as e:
            print(f"Ping failed: {e}")
        time.sleep(60)  # Ping every minute

# Start the ping system in a background thread
threading.Thread(target=auto_ping, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
