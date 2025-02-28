import logging
from src.operations.ask import LLMAsker
from src.operations.search import SearchEngine
from src.operations.embed import EmbedService
from src.operations.extract import MarkdownExtractor

# Optional: Set up package-level logging if needed
logging.basicConfig(level=logging.INFO)