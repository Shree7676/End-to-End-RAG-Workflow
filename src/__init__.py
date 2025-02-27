import logging
from src.operations.ask import LLMAsker
from src.operations.search import SearchEngine
from src.operations.embed import EmbedService
from src.operations.extract import MarkdownExtractor
from src.app import App  # Import App from main.py for convenience

# Optional: Set up package-level logging if needed
logging.basicConfig(level=logging.INFO)