#!/usr/bin/env python3
"""
Script to ingest PDF and build vector index
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from hr_agent.pdf_ingest import extract_pdf
from hr_agent.chunking import create_chunker
from hr_agent.embeddings import create_embedding_model
from hr_agent.vectordb import create_vectordb
from hr_agent.utils import get_logger

logger = get_logger(__name__)

def main():
    """Ingest PDF and build vector index"""
    print("=" * 60)
    print("PDF INGESTION & VECTOR INDEX BUILD")
    print("=" * 60)

    # Check if PDF exists
    if not config.PDF_PATH.exists():
        logger.error(f"PDF not found at: {config.PDF_PATH}")
        logger.error("Please place the Arabic PDF at this location.")
        return 1

    # Check if embedding model exists
    if not config.EMBED_MODEL_PATH.exists():
        logger.error(f"Embedding model not found at: {config.EMBED_MODEL_PATH}")
        logger.error("Please download the embedding model and place it at this location.")
        return 1

    try:
        # Step 1: Extract PDF
        logger.info("Step 1: Extracting PDF pages...")
        pages = extract_pdf(config.PDF_PATH)
        logger.info(f"✓ Extracted {len(pages)} pages")

        # Step 2: Chunk text
        logger.info("Step 2: Chunking text...")
        chunker = create_chunker(
            min_words=config.CHUNK_MIN_WORDS,
            max_words=config.CHUNK_MAX_WORDS,
            overlap_words=config.CHUNK_OVERLAP_WORDS
        )
        chunks = chunker.chunk_pages(pages)
        logger.info(f"✓ Created {len(chunks)} chunks")

        # Step 3: Load embedding model
        logger.info("Step 3: Loading embedding model...")
        embedding_model = create_embedding_model(
            config.EMBED_MODEL_PATH,
            device=config.DEVICE_PREFERENCE
        )
        logger.info("✓ Embedding model loaded")

        # Step 4: Create/load vector database
        logger.info("Step 4: Initializing vector database...")
        vectordb = create_vectordb(
            config.CHROMA_DIR,
            config.CHROMA_COLLECTION_NAME,
            embedding_model
        )

        # Check if already populated
        existing_count = vectordb.count()
        if existing_count > 0:
            logger.warning(f"Collection already has {existing_count} chunks")
            response = input("Do you want to reset and rebuild? (yes/no): ").strip().lower()
            if response == "yes":
                vectordb.reset()
                logger.info("Collection reset")
            else:
                logger.info("Keeping existing index")
                return 0

        # Step 5: Add chunks to vector database
        logger.info("Step 5: Adding chunks to vector database...")
        vectordb.add_chunks(chunks, show_progress=True)
        logger.info(f"✓ Added {len(chunks)} chunks to vector database")

        # Verify
        final_count = vectordb.count()
        logger.info(f"✓ Final chunk count: {final_count}")

        print("\n" + "=" * 60)
        print("PDF INGESTION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"PDF Pages:     {len(pages)}")
        print(f"Total Chunks:  {final_count}")
        print(f"Storage:       {config.CHROMA_DIR}")
        print("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"Failed to ingest PDF: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
