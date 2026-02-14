"""
Vector database module using ChromaDB
"""
from typing import List, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from hr_agent.schemas import Chunk, RetrievedChunk
from hr_agent.embeddings import EmbeddingModel
from hr_agent.utils import get_logger

logger = get_logger(__name__)

class VectorDB:
    """
    ChromaDB wrapper for document storage and retrieval
    """

    def __init__(
        self,
        persist_directory: Path,
        collection_name: str,
        embedding_model: Optional[EmbeddingModel] = None
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model

        # Ensure directory exists
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"✓ Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Saudi Labor Policy Documents"}
            )
            logger.info(f"✓ Created new collection: {self.collection_name}")

    def add_chunks(self, chunks: List[Chunk], show_progress: bool = True):
        """
        Add chunks to the vector database
        """
        if not chunks:
            logger.warning("No chunks to add")
            return

        # Prepare data
        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "chunk_id": chunk.chunk_id,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "source": chunk.source
            }
            for chunk in chunks
        ]

        # Generate embeddings if model is available
        embeddings = None
        if self.embedding_model:
            logger.info(f"Generating embeddings for {len(chunks)} chunks...")
            texts = [chunk.text for chunk in chunks]
            embeddings = self.embedding_model.encode(texts, show_progress=show_progress)

        # Add to ChromaDB
        logger.info(f"Adding {len(chunks)} chunks to ChromaDB...")
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        logger.info("✓ Chunks added successfully")

    def search(
        self,
        query: str,
        top_k: int = 6
    ) -> List[RetrievedChunk]:
        """
        Search for relevant chunks
        """
        # Generate query embedding if model is available
        query_embedding = None
        if self.embedding_model:
            query_embedding = self.embedding_model.encode_single(query)

        # Query ChromaDB
        results = self.collection.query(
            query_texts=[query] if query_embedding is None else None,
            query_embeddings=[query_embedding] if query_embedding else None,
            n_results=top_k
        )

        # Parse results
        retrieved_chunks = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                chunk_id = results['ids'][0][i]
                document = results['documents'][0][i]
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i] if 'distances' in results else 0.0

                # Convert distance to similarity score (lower distance = higher similarity)
                score = 1.0 / (1.0 + distance)

                retrieved_chunk = RetrievedChunk(
                    chunk_id=chunk_id,
                    text=document,
                    page_start=metadata.get('page_start', 0),
                    page_end=metadata.get('page_end', 0),
                    source=metadata.get('source', 'unknown'),
                    score=score
                )
                retrieved_chunks.append(retrieved_chunk)

        logger.info(f"Retrieved {len(retrieved_chunks)} chunks for query")
        return retrieved_chunks

    def count(self) -> int:
        """Get total number of chunks in collection"""
        return self.collection.count()

    def reset(self):
        """Delete all chunks from collection"""
        logger.warning(f"Resetting collection: {self.collection_name}")
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Saudi Labor Policy Documents"}
        )
        logger.info("✓ Collection reset")

def create_vectordb(
    persist_directory: Path,
    collection_name: str,
    embedding_model: Optional[EmbeddingModel] = None
) -> VectorDB:
    """Factory function to create vector database"""
    return VectorDB(persist_directory, collection_name, embedding_model)
