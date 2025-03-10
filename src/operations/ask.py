import logging
from .chromadb_client import chroma_db
from .search import SearchEngine  
from src.api import execute_prompt
import re

logger = logging.getLogger('llm-asker')

class LLMAsker:
    def __init__(self):
        logger.info('LLMAsker initialized')
        self.collection = chroma_db.collection
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

    def ask(self, query: str, top_k: int = 3) -> list[str]:
        """Query the LLM with the provided query and retrieved document context."""
        logger.info(f"Asking LLM with query: '{query}'")
        try:
            # Build context from retrieved documents
            context = self.build_context(query, top_k)

            # Prepare the prompt
            prompt = f"""
            You are an assistant. Use the following context to answer the question accurately and concisely.
            Context may be in any language, but your answer MUST be in the same language as the question.
            I repeat this is very important you should response in same language as Question.
            
            Context:
            {context}

            Question: {query}
            Answer:
            """
            # Execute the prompt
            api_response = execute_prompt(prompt)
            answer = api_response.get('response', 'Error: No response from API')
            logger.info("LLM response generated successfully")
            return [answer,context]
        except Exception as e:
            logger.error(f"Failed to query LLM: {str(e)}")
            return f"Error processing query: {str(e)}"
        
    

# Example usage
if __name__ == "__main__":
    # Configure logging to see output
    logging.basicConfig(level=logging.INFO)

    asker = LLMAsker()
    
    query = "Q1-Q4 Projects result"
    answer,context = asker.ask(query)
    logger.info(f"LLM Answer: {answer}")