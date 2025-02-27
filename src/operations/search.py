import logging
from typing import List
import chromadb
from src.api import embed_texts

# Set up logging consistent with previous classes
logger = logging.getLogger('search-engine')

class SearchEngine:
    def __init__(self):
        """Initialize the SearchEngine."""
        logger.info('SearchEngine initialized')
        # Initialize ChromaDB client and collection
        self.vector_db_path = "vectorDB"
        self.chroma_client = chromadb.PersistentClient(path=self.vector_db_path)
        self.collection = self.chroma_client.get_collection(name="my_collection")

    def embed_query(self, query: str) -> List[float]:
        """Generate an embedding for the search query."""
        logger.info(f"Generating embedding for query: '{query}'")
        try:
            embedding = embed_texts([query], 'query')[0]
            logger.debug("Query embedding generated successfully")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {str(e)}")
            raise

    def search(self, query: str, top_k: int = 3) -> List[str]:
        """Search the vectorDB and return the filenames of the top matching documents."""
        logger.info(f"Searching vectorDB for query: '{query}' with top_k={top_k}")
        try:
            query_embedding = self.embed_query(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            matching_ids = results['ids'][0]  # List of filenames (ids)
            logger.info(f"Found {len(matching_ids)} matching documents: {matching_ids}")
            return matching_ids
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

# Example usage
if __name__ == "__main__":
    # Configure logging to see output
    logging.basicConfig(level=logging.INFO)

    search_engine = SearchEngine()
    
    query = "The Loan Amount shall be transferred within how many days?"
    matching_files = search_engine.search(query)
    logger.info(f"Matching Filenames: {matching_files}")