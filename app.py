from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import base64
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key

REIMAGINE_API_KEY = '922c7ff9711a18fefd84c8a2fda99815ae885baf1ae3b65b9a5edadd8978caaa2ab57d63ae4399349f828a419fa01468'
REIMAGINE_API_URL = 'https://clipdrop-api.co/reimagine/v1/reimagine'

def reimagine_image(image_file):
    files = {'image_file': ('uploaded_image.jpg', image_file.read(), 'image/jpeg')}
    headers = {'x-api-key': REIMAGINE_API_KEY}

    # Make three requests with different variations
    variations = []
    for _ in range(3):
        response = requests.post(REIMAGINE_API_URL, files=files, headers=headers)

        if response.ok:
            variations.append(base64.b64encode(response.content).decode('utf-8'))
        else:
            try:
                error_message = response.json()['error']
            except (ValueError, KeyError):
                error_message = response.text

            raise Exception(f"Reimagine API error: {response.status_code} - {error_message}")

    return variations


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        

        try:
            reimagined_variations = reimagine_image(file)
            srcfile = request.files.get('file')
            filename = secure_filename(srcfile.filename)
            pathfile = f"static/uploads/{filename}"
            srcfile.save(pathfile)
            return render_template('result.html', reimagined_variations=reimagined_variations, pathfile=pathfile)
        except Exception as e:
            flash(str(e), 'error')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
