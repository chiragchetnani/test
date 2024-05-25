from flask import Flask, render_template, request, jsonify
from discriminator import categorize_files
from doc_extract import pdf, docx_, pptx, csv, txt
from image_extract import image_text
from video_extract import video_transcript
import os
from answer import answer

app = Flask(__name__)
UPLOAD_FOLDER = 'temp_uploaded'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to process files based on type
def process_files(uploaded_files):
    context_text = ''
    # Process each uploaded file
    for uploaded_file in uploaded_files:
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
        
        # Check file extension and process accordingly
        file_ext = file_path.split('.')[-1].lower()
        if file_ext in ['pdf', 'docx', 'doc', 'pptx', 'csv', 'txt']:
            if file_ext == 'pdf':
                context_text += pdf(file_path)
            elif file_ext in ['docx', 'doc']:
                context_text += docx_(file_path)
            elif file_ext == 'pptx':
                context_text += pptx(file_path)
            elif file_ext == 'csv':
                context_text += csv(file_path)
            elif file_ext == 'txt':
                context_text += txt(file_path)
        elif file_ext in ['jpg', 'png', 'jpeg']:
            context_text += image_text(file_path)
        elif file_ext == 'mp4':
            context_text += video_transcript(file_path)

        # Optionally delete the file after processing if not needed
        os.remove(file_path)
    return context_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400
    
    files = request.files.getlist('files[]')
    context_text = process_files(files)
    return jsonify({'context_text': context_text})

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '')
    context_text = data.get('context_text', '')
    response = answer(question, context_text)
    return jsonify({'response': response})

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
