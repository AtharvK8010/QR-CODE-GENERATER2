from flask import Flask, render_template, request, send_file, url_for
import qrcode
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates", static_folder="static")

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.form.get('data')
    file = request.files.get('file')

    if not data and not file:
        return "Error: No data or file provided!", 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        data = url_for('static', filename=f'uploads/{filename}', _external=True)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img_path = os.path.join(UPLOAD_FOLDER, "qrcode.png")
    img = qr.make_image(fill='black', back_color='white')
    img.save(qr_img_path)

    return send_file(qr_img_path, mimetype='image/png', as_attachment=True, download_name='qrcode.png')

if __name__ == '__main__':
    app.run(debug=True)
