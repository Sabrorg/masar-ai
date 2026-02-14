"""
Text chunking module for Arabic documents
"""
from typing import List, Tuple
from hr_agent.schemas import Chunk
from hr_agent.utils import count_arabic_words, clean_arabic_text, generate_chunk_id, get_logger

logger = get_logger(__name__)

class ArabicChunker:
    """
    Word-based chunker optimized for Arabic text
    """

    def __init__(
        self,
        min_words: int = 150,
        max_words: int = 220,
        overlap_words: int = 50
    ):
        self.min_words = min_words
        self.max_words = max_words
        self.overlap_words = overlap_words

    def chunk_text(
        self,
        text: str,
        page_num: int,
        source: str = "saudi_labor_bylaws_pdf"
    ) -> List[Chunk]:
        """
        Chunk text into overlapping segments
        """
        # Clean text
        text = clean_arabic_text(text)

        if not text.strip():
            return []

        # Split into words
        words = text.split()
        total_words = len(words)

        if total_words == 0:
            return []

        chunks = []
        chunk_index = 0
        start_idx = 0

        while start_idx < total_words:
            # Determine chunk end
            end_idx = min(start_idx + self.max_words, total_words)

            # Extract chunk words
            chunk_words = words[start_idx:end_idx]
            chunk_text = " ".join(chunk_words)

            # Generate chunk ID
            chunk_id = generate_chunk_id(page_num, chunk_index, chunk_text)

            # Create chunk object
            chunk = Chunk(
                chunk_id=chunk_id,
                text=chunk_text,
                page_start=page_num,
                page_end=page_num,
                source=source
            )
            chunks.append(chunk)

            # Move start index forward with overlap
            if end_idx >= total_words:
                break

            start_idx = end_idx - self.overlap_words
            chunk_index += 1

        logger.debug(f"Page {page_num}: {total_words} words -> {len(chunks)} chunks")
        return chunks

    def chunk_pages(
        self,
        pages: List[Tuple[int, str]],
        source: str = "saudi_labor_bylaws_pdf"
    ) -> List[Chunk]:
        """
        Chunk multiple pages
        Args:
            pages: List of (page_num, text) tuples
            source: Source identifier
        Returns:
            List of chunks
        """
        all_chunks = []

        for page_num, text in pages:
            page_chunks = self.chunk_text(text, page_num, source)
            all_chunks.extend(page_chunks)

        logger.info(f"Chunked {len(pages)} pages into {len(all_chunks)} chunks")
        return all_chunks

def create_chunker(min_words: int = 150, max_words: int = 220, overlap_words: int = 50) -> ArabicChunker:
    """Factory function to create chunker"""
    return ArabicChunker(min_words, max_words, overlap_words)
