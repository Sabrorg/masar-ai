"""
Utility functions for HR Assistant
"""
import re
import hashlib
import logging
from typing import List
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str):
    """Get logger instance"""
    return logging.getLogger(name)

def clean_arabic_text(text: str) -> str:
    """
    Clean Arabic text from PDF extraction artifacts
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove common PDF artifacts
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    # Fix broken lines (remove hyphenation at line breaks)
    text = re.sub(r'-\s*\n\s*', '', text)

    # Normalize Arabic characters
    text = text.replace('ـ', '')  # Remove tatweel

    # Strip leading/trailing whitespace
    text = text.strip()

    return text

def count_arabic_words(text: str) -> int:
    """
    Count words in Arabic text
    Works for both Arabic and mixed Arabic-English text
    """
    # Split on whitespace and count non-empty tokens
    words = text.split()
    return len([w for w in words if w.strip()])

def generate_chunk_id(page_num: int, chunk_index: int, text_snippet: str) -> str:
    """
    Generate deterministic chunk ID
    """
    # Use first 50 chars of text for stability
    snippet = text_snippet[:50]
    content = f"page{page_num}_chunk{chunk_index}_{snippet}"
    hash_obj = hashlib.md5(content.encode('utf-8'))
    return f"chunk_{page_num}_{chunk_index}_{hash_obj.hexdigest()[:8]}"

def get_device(preference: str = "cuda") -> str:
    """
    Get available device (cuda or cpu)
    """
    if preference == "cuda" and torch.cuda.is_available():
        return "cuda"
    return "cpu"

def format_salary(amount: float) -> str:
    """Format salary in SAR"""
    return f"{amount:,.2f} ريال"

def format_employee_info(employee) -> str:
    """
    Format employee information for display
    """
    lines = [
        f"الاسم: {employee.full_name_ar}",
        f"الرقم الوظيفي: {employee.employee_id}",
        f"القسم: {employee.department}",
        f"المسمى الوظيفي: {employee.job_title_ar}",
        f"الدرجة: {employee.grade_level}",
        f"الراتب الأساسي: {format_salary(employee.base_salary_sar)}",
        f"البدلات: {format_salary(employee.allowances_sar)}",
        f"إجمالي الراتب: {format_salary(employee.total_salary_sar)}",
        f"التقييم السنوي: {employee.performance_rating_year}/5",
        f"ملاحظات الأداء: {employee.performance_notes_ar}",
        f"الهدف السنوي: {employee.yearly_goal_title_ar}",
        f"مؤشرات الأداء: {employee.yearly_goal_kpis_ar}",
    ]

    if employee.last_month_deductions_sar > 0:
        lines.append(f"الخصومات الشهر الماضي: {format_salary(employee.last_month_deductions_sar)}")

    if employee.warnings_count > 0:
        lines.append(f"عدد الإنذارات: {employee.warnings_count}")

    return "\n".join(lines)

def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def is_arabic(text: str) -> bool:
    """Check if text contains Arabic characters"""
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))
