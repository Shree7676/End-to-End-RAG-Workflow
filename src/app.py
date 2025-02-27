import logging
import argparse
import os
from pathlib import Path
from src.operations.extract import MarkdownExtractor
from src.operations.embed import EmbedService
from src.operations.search import SearchEngine
from src.operations.ask import LLMAsker

# Set up logging
logger = logging.getLogger('app')

class App:
    """The main class of the application."""

    def __init__(self):
        """Initialize the App with all operators."""
        logger.info("Initializing App")
        self.extractor = MarkdownExtractor()
        self.embedder = EmbedService()
        self.searcher = SearchEngine()
        self.asker = LLMAsker()
        self.input_dir = Path("documents")  # Where mixed files live
        self.md_dir = Path("output_md")     # Where Markdown files go

    def run(self):
        """Parse arguments and run the selected mode."""
        parser = argparse.ArgumentParser(description='Ask questions about the files of a case.')
        parser.add_argument('--mode', choices=['index-files', 'ask-question', 'search', 'get-markdown'], 
                           default='ask-question', help='The mode of the application.')
        parser.add_argument('question', nargs='?', type=str, 
                           help='The question or query for ask-question or search mode.')

        args = parser.parse_args()

        if args.mode == 'index-files':
            self.index_files()
        elif args.mode == 'ask-question':
            question = args.question
            if not question or question.isspace():
                parser.error('The question argument is required in "ask-question" mode.')
            self.ask_question(question)
        elif args.mode == 'search':
            query = args.question
            if not query or query.isspace():
                parser.error('The query argument is required in "search" mode.')
            self.search(query)
        elif args.mode == 'get-markdown':
            self.get_markdown()

    def get_markdown(self):
        """Convert all files in documents/ to Markdown."""
        logger.info("Starting get-markdown mode")
        if not self.input_dir.exists():
            logger.error(f"Input directory {self.input_dir} does not exist")
            return

        for file_path in self.input_dir.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() != ".md":
                logger.info(f"Converting {file_path}")
                self.extractor.extract(str(file_path))

        logger.info("Markdown conversion complete")

    def index_files(self):
        """Load and index Markdown files into the vector database."""
        logger.info("Starting index-files mode")
        if not self.md_dir.exists():
            logger.error(f"Markdown directory {self.md_dir} does not exist. Run get-markdown first.")
            return

        md_files = [str(file_path) for file_path in self.md_dir.glob("*.md")]
        if not md_files:
            logger.warning(f"No Markdown files found in {self.md_dir}")
            return

        self.embedder.store_files(md_files)
        logger.info("Files indexed successfully")

    def search(self, query: str):
        """Search the indexed files for results matching the query."""
        logger.info(f"Searching for query: '{query}'")
        matching_files = self.searcher.search(query)
        if matching_files:
            print("Matching Filenames:", matching_files)
            logger.info(f"Found matches: {matching_files}")
        else:
            print("No matching files found.")
            logger.info("No matches found")

    def ask_question(self, question: str):
        """Ask a question using the LLM with context from indexed files."""
        logger.info(f"Asking question: '{question}'")
        response = self.asker.ask(question)
        print("LLM Answer:", response)
        logger.info("Question answered successfully")

# Entry point
if __name__ == "__main__":
    app = App()
    app.run()