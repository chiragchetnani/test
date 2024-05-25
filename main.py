import streamlit as st
from discriminator import categorize_files
from doc_extract import pdf, docx_, pptx, csv, txt
from image_extract import image_text
from video_extract import video_transcript
import os
from answer import answer

# Function to process files based on type
def process_files(uploaded_files):
    context_text = ''
    # Save uploaded files to a temporary directory
    temp_dir = "temp_uploaded"
    os.makedirs(temp_dir, exist_ok=True)

    # Process each uploaded file
    for uploaded_file in uploaded_files:
        # Save the file
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
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

# Streamlit UI
st.title('File-Based Chatbot Interface')

# File uploader allows user to upload multiple files of specified types
uploaded_files = st.file_uploader("Upload your files", type=['pdf', 'docx', 'pptx', 'csv', 'txt', 'jpg', 'png', 'mp4'], accept_multiple_files=True)

if uploaded_files:
    # Process the files

    with open('temp.txt' , 'w') as context_file : context_file.write(process_files(uploaded_files))

    # Simple chatbot interaction
    user_input = st.text_input("Ask me anything based on the uploaded content:")
    if user_input:
        # Dummy response mechanism (you could integrate a real model or logic here)
        # st.write("Response:", "This is a placeholder response to the question:", user_input)
        st.write(answer(user_input))