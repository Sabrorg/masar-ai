"""
PDF ingestion module for Arabic documents
"""
from typing import List, Tuple
from pathlib import Path
from hr_agent.utils import clean_arabic_text, get_logger

logger = get_logger(__name__)

class PDFExtractor:
    """
    Extract text from PDF files (Arabic-optimized)
    """

    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path

    def extract_pages(self) -> List[Tuple[int, str]]:
        """
        Extract text from all pages
        Returns:
            List of (page_number, text) tuples (1-indexed)
        """
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {self.pdf_path}")

        # Try PyMuPDF first
        try:
            import fitz  # PyMuPDF
            return self._extract_with_pymupdf()
        except ImportError:
            logger.warning("PyMuPDF not available, trying pdfplumber")
            try:
                import pdfplumber
                return self._extract_with_pdfplumber()
            except ImportError:
                raise ImportError(
                    "No PDF library available. Install PyMuPDF (fitz) or pdfplumber:\n"
                    "  pip install pymupdf\n"
                    "  or\n"
                    "  pip install pdfplumber"
                )

    def _extract_with_pymupdf(self) -> List[Tuple[int, str]]:
        """Extract using PyMuPDF (preferred for Arabic)"""
        import fitz

        doc = fitz.open(self.pdf_path)
        pages = []

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_text()
            text = clean_arabic_text(text)

            # Page number is 1-indexed
            page_num = page_idx + 1
            pages.append((page_num, text))

        doc.close()
        logger.info(f"Extracted {len(pages)} pages using PyMuPDF")
        return pages

    def _extract_with_pdfplumber(self) -> List[Tuple[int, str]]:
        """Extract using pdfplumber (fallback)"""
        import pdfplumber

        pages = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                text = clean_arabic_text(text)

                # Page number is 1-indexed
                page_num = page_idx + 1
                pages.append((page_num, text))

        logger.info(f"Extracted {len(pages)} pages using pdfplumber")
        return pages

def extract_pdf(pdf_path: Path) -> List[Tuple[int, str]]:
    """
    Convenience function to extract PDF pages
    """
    extractor = PDFExtractor(pdf_path)
    return extractor.extract_pages()
