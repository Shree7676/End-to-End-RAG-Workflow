import logging
import chromadb
from .search import SearchEngine  # Relative import within src/operations/
from src.api import execute_prompt

# Set up logging
logger = logging.getLogger('llm-asker')

class LLMAsker:
    def __init__(self):
        """Initialize the LLMAsker."""
        logger.info('LLMAsker initialized')
        # Initialize ChromaDB client and collection
        self.vector_db_path = "vectorDB"
        self.chroma_client = chromadb.PersistentClient(path=self.vector_db_path)
        try:
            self.collection = self.chroma_client.get_collection(name="my_collection")
        except Exception as e:
            logger.error(f"Failed to connect to collection 'my_collection': {str(e)}")
            raise
        # Initialize SearchEngine instance
        self.search_engine = SearchEngine()

    def build_context(self, query: str, top_k: int = 3) -> str:
        """Search for matching documents and build context for the LLM."""
        logger.info(f"Building context for query: '{query}' with top_k={top_k}")
        try:
            # Search for matching filenames
            matching_files = self.search_engine.search(query, top_k)
            if not matching_files:
                logger.warning("No matching files found for query")
                return "No relevant documents found in the database."

            # Retrieve full documents from ChromaDB
            results = self.collection.get(ids=matching_files)
            retrieved_docs = results['documents'] or []

            if not retrieved_docs:
                logger.warning("No document contents retrieved for matching files")
                return "Documents found but no content retrieved."

            # Format context
            context = "\n\n".join([f"Document '{doc_id}':\n{content}" 
                                 for doc_id, content in zip(matching_files, retrieved_docs)])
            logger.debug(f"Context built with {len(matching_files)} documents")
            return context
        except Exception as e:
            logger.error(f"Failed to build context: {str(e)}")
            return f"Error retrieving documents: {str(e)}"

    def ask(self, query: str, top_k: int = 3) -> str:
        """Query the LLM with the provided query and retrieved document context."""
        logger.info(f"Asking LLM with query: '{query}'")
        try:
            # Build context from retrieved documents
            context = self.build_context(query, top_k)

            # Prepare the prompt
            prompt = f"""
            You are an assistant. Use the following context to answer the question accurately and concisely.
            answer in English
            
            Context:
            {context}

            Question: {query}
            Answer:
            """
            # Execute the prompt
            answer = execute_prompt(prompt)
            logger.info("LLM response generated successfully")
            return answer
        except Exception as e:
            logger.error(f"Failed to query LLM: {str(e)}")
            return f"Error processing query: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Configure logging to see output
    logging.basicConfig(level=logging.INFO)

    asker = LLMAsker()
    
    query = "Q1-Q4 Projects result"
    answer = asker.ask(query)
    logger.info(f"LLM Answer: {answer}")