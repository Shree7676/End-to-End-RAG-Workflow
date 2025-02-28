from flask import Flask, render_template, request, jsonify, redirect,url_for
from src.operations.ask import LLMAsker
from src.operations.embed import EmbedService
from src.operations.extract import MarkdownExtractor
import os
import re

asker = LLMAsker()

app = Flask(__name__)

user_messages = []

files = [
        "0664411829.pdf",
        "Company OKRs.xlsx",
        "Scan EVB IT-Cloud Vertrag.pdf",
        "Übermittlung Finanzamt.pdf",
        "CLA_filled.docx",
        "NDA_filled.docx",
        "Scan 10.08.2023.pdf",
        "Scan Stromtarif.pdf",
        "WG Anfrage Veröffentlichung Gerichtsurteile.msg"
    ]

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", user_messages=user_messages, files=files)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form["question"]
    user_messages.append((user_message, 'user'))
    bot_response,retrived_data = asker.ask(user_message)
    bot_response = format_llm_response(bot_response)
    user_messages.append((bot_response, 'bot'))
    return render_template("index.html", user_messages=user_messages,files=files,retrived_data=str(retrived_data))



def format_llm_response(raw_response):
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', raw_response)
    formatted = formatted.replace('<br>', '<br>')
    return formatted


# @app.route("/", methods=["POST"])
# @app.route("/chat", methods=["POST"])
# def upload():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
    
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
    
#     if file:
#         # Save the uploaded file to a temporary location
#         upload_folder = "uploads"
#         os.makedirs(upload_folder, exist_ok=True)
#         filepath = os.path.join(upload_folder, file.filename)
#         file.save(filepath)
        
#         try:
#             # Create instance of EmbedService and store directly
#             embed_service = EmbedService()
#             embed_service.store_files(filepath)
            
#             # Update the files list
#             files.append(file.filename)
            
#             return jsonify({
#                 'message': 'File uploaded and embedded successfully',
#                 'filename': file.filename
#             }), 200
            
#         except Exception as e:
#             return jsonify({'error': str(e)}), 500
        
#         finally:
#             # Clean up the temporary file
#             if os.path.exists(filepath):
#                 os.remove(filepath)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)