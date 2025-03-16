from flask import Flask, render_template, request, send_file, url_for, jsonify
import qrcode
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates", static_folder="static")

UPLOAD_FOLDER = "static/uploads"
QR_FOLDER = "saved_qr_codes"
DB_FILE = "qr_codes.json"

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["QR_FOLDER"] = QR_FOLDER

# Load or create QR database
def load_qr_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as file:
            return json.load(file)
    return {}

def save_qr_data(qr_data):
    with open(DB_FILE, "w") as file:
        json.dump(qr_data, file, indent=4)

qr_data = load_qr_data()

@app.route('/')
def home():  # Renamed 'index' to 'home' to avoid conflicts
    return render_template('index.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.form.get('data')
    file = request.files.get('file')
    qr_name = request.form.get('qr_name', '').strip()

    if not data and not file:
        return jsonify({"error": "No data or file provided!"}), 400

    # If a file is uploaded, save it and generate a download link
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        data = url_for('static', filename=f'uploads/{filename}', _external=True)

    # Use existing QR if available
    if data in qr_data:
        qr_filename = qr_data[data]
    else:
        if not qr_name:
            qr_name = f"qr_{len(qr_data) + 1}"
        qr_filename = f"{qr_name}.png"
        qr_img_path = os.path.join(QR_FOLDER, qr_filename)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        img.save(qr_img_path)

        qr_data[data] = qr_filename
        save_qr_data(qr_data)

    qr_img_path = os.path.join(QR_FOLDER, qr_filename)
    return send_file(qr_img_path, mimetype='image/png', as_attachment=True, download_name=qr_filename)

@app.route('/get_qr_list')
def get_qr_list():
    return jsonify(qr_data)

if __name__ == '__main__':
    app.run(debug=True)
