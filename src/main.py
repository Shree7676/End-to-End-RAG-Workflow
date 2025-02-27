import logging
import os
from flask import Flask, request, render_template, jsonify
from src.operations.extract import MarkdownExtractor
from src.operations.embed import EmbedService
from src.operations.search import SearchEngine
from src.operations.ask import LLMAsker
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('app')

# Set template folder dynamically
template_dir = Path(__file__).parent / "templates"
app_flask = Flask(__name__, template_folder=str(template_dir))

class App:
    def __init__(self):
        logger.info("Initializing App")
        self.extractor = MarkdownExtractor()
        self.embedder = EmbedService()
        self.searcher = SearchEngine()
        self.asker = LLMAsker()
        self.input_dir = Path("documents")
        self.md_dir = Path("output_md")

    def get_markdown(self):
        logger.info("Starting get-markdown mode")
        if not self.input_dir.exists():
            return "Input directory does not exist"
        for file_path in self.input_dir.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() != ".md":
                self.extractor.extract(str(file_path))
        return "Markdown conversion complete"

    def index_files(self):
        logger.info("Starting index-files mode")
        if not self.md_dir.exists():
            return "Markdown directory does not exist. Run get-markdown first."
        md_files = [str(file_path) for file_path in self.md_dir.glob("*.md")]
        if not md_files:
            return "No Markdown files found"
        self.embedder.store_files(md_files)
        return "Files indexed successfully"

    def search(self, query: str):
        logger.info(f"Searching for query: '{query}'")
        return self.searcher.search(query)

    def ask_question(self, question: str):
        logger.info(f"Asking question: '{question}'")
        return self.asker.ask(question)

# Flask routes
@app_flask.route('/', methods=['GET', 'POST'])
def index():
    app_instance = App()
    result = None
    if request.method == 'POST':
        mode = request.form.get('mode')
        query = request.form.get('query', '').strip()
        
        if mode == 'get-markdown':
            result = app_instance.get_markdown()
        elif mode == 'index-files':
            result = app_instance.index_files()
        elif mode == 'search':
            if not query:
                result = "Query required for search"
            else:
                result = ", ".join(app_instance.search(query)) or "No matches found"
        elif mode == 'ask-question':
            if not query:
                result = "Question required"
            else:
                result = app_instance.ask_question(query)
    
    return render_template('index.html', result=result)

# Export Flask app for Vercel and allow local testing
app = app_flask

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)