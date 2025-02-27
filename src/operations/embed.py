import chromadb
import logging
import os
from src.api import embed_texts
from typing import List
from pathlib import Path

# Set up logging consistent with MarkdownExtractor
logger = logging.getLogger('embed-service')

class EmbedService:
    def __init__(self):
        """Initialize the EmbedService."""
        logger.info('EmbedService initialized')
        # Initialize ChromaDB client and collection
        self.vector_db_path = "vectorDB"
        self.chroma_client = chromadb.PersistentClient(path=self.vector_db_path)
        self.collection = self.chroma_client.get_or_create_collection(name="my_collection")
        # Set input folder for Markdown files
        self.input_folder = Path(__file__).parent / "../../output_md"
        os.makedirs(self.input_folder, exist_ok=True)

    def embed(self, text: str) -> List[float]:
        """Generate embeddings for a single text."""
        logger.info(f"Generating embedding for text (length: {len(text)} characters)")
        try:
            embedding = embed_texts([text], 'document')[0]
            logger.debug("Embedding generated successfully")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise

    def load_and_embed_file(self, file_path: str) -> tuple:
        """Load a single file and generate its embedding."""
        logger.info(f"Processing file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text_data = file.read()
            file_name = os.path.basename(file_path)
            embedding = self.embed(text_data)
            return text_data, {"file_name": file_name}, file_name, embedding
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
            return None, None, None, None
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return None, None, None, None

    def store_files(self, file_paths: List[str]):
        """Process multiple files and store them in the vector database."""
        logger.info(f"Starting to process {len(file_paths)} files for embedding")
        
        documents, metadatas, ids, embeddings = [], [], [], []
        
        for file_path in file_paths:
            doc, meta, id_, emb = self.load_and_embed_file(file_path)
            if doc and emb:  # Only add if successfully processed
                documents.append(doc)
                metadatas.append(meta)
                ids.append(id_)
                embeddings.append(emb)

        if embeddings:
            logger.info(f"Storing {len(embeddings)} documents in VectorDB")
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            logger.info("Data successfully stored in VectorDB!")
        else:
            logger.warning("No embeddings generated to store in VectorDB")

# Example usage
if __name__ == "__main__":
    # Configure logging to see output
    logging.basicConfig(level=logging.INFO)

    embed_service = EmbedService()
    
    # List of Markdown files from output_md folder
    file_names = [
        '0664411829.md',
        'Company OKRs.md',
        'Scan EVB IT-Cloud Vertrag.md',
        'Übermittlung Finanzamt.md',
        'CLA_filled.md',
        'NDA_filled.md',
        'Scan 10.08.2023.md',
        'Scan Stromtarif.md',
        'WG Anfrage Veröffentlichung Gerichtsurteile.md'
    ]
    
    file_paths = [os.path.join(embed_service.input_folder, fn) for fn in file_names]
    embed_service.store_files(file_paths)