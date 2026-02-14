"""
Data schemas for HR Assistant
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import date

@dataclass
class Chunk:
    """Represents a document chunk"""
    chunk_id: str
    text: str
    page_start: int
    page_end: int
    source: str = "saudi_labor_bylaws_pdf"
    embedding: Optional[List[float]] = None

    def to_chroma_dict(self):
        """Convert to ChromaDB format"""
        return {
            "id": self.chunk_id,
            "document": self.text,
            "metadata": {
                "chunk_id": self.chunk_id,
                "page_start": self.page_start,
                "page_end": self.page_end,
                "source": self.source,
            }
        }

@dataclass
class RetrievedChunk:
    """Chunk with retrieval score"""
    chunk_id: str
    text: str
    page_start: int
    page_end: int
    source: str
    score: float

    def citation(self) -> str:
        """Generate citation string"""
        if self.page_start == self.page_end:
            return f"صفحة {self.page_start} (chunk_id={self.chunk_id})"
        else:
            return f"صفحات {self.page_start}-{self.page_end} (chunk_id={self.chunk_id})"

@dataclass
class Employee:
    """Employee record"""
    employee_id: str
    full_name_ar: str
    department: str
    job_title_ar: str
    grade_level: int
    manager_id: Optional[str]
    hire_date: date
    base_salary_sar: float
    allowances_sar: float
    total_salary_sar: float
    performance_rating_year: int
    performance_notes_ar: str
    yearly_goal_title_ar: str
    yearly_goal_kpis_ar: str
    training_plan_ar: str
    last_promotion_date: Optional[date]
    warnings_count: int
    last_month_deductions_sar: float

@dataclass
class QueryRoute:
    """Query routing decision"""
    route_type: str  # "db", "rag", "hybrid"
    confidence: float
    reasoning: str
