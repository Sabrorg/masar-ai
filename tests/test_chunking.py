"""
Test chunking functionality
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hr_agent.chunking import create_chunker
from hr_agent.utils import count_arabic_words

def test_chunking():
    """Test basic chunking"""
    print("Testing chunking...")

    # Create chunker
    chunker = create_chunker(min_words=150, max_words=220, overlap_words=50)

    # Test text (Arabic lorem ipsum)
    test_text = """
    تنص المادة الأولى من نظام العمل السعودي على أن هذا النظام يهدف إلى تنظيم العلاقة بين صاحب العمل والعامل
    وتحديد حقوق وواجبات كل منهما. ويشمل النظام جميع العمال والموظفين في القطاع الخاص.
    المادة الثانية تحدد ساعات العمل اليومية والأسبوعية. حيث لا يجوز أن تزيد ساعات العمل الفعلية عن ثماني ساعات
    يوميا إذا اعتمد صاحب العمل المعيار اليومي، أو ثمان وأربعين ساعة في الأسبوع إذا اعتمد المعيار الأسبوعي.
    المادة الثالثة تنص على حق العامل في الحصول على إجازة سنوية مدفوعة الأجر لا تقل عن واحد وعشرين يوما
    لكل عام، تزاد إلى ثلاثين يوما إذا أمضى العامل في خدمة صاحب العمل خمس سنوات متصلة.
    """ * 10  # Repeat to get enough text

    # Chunk the text
    chunks = chunker.chunk_text(test_text, page_num=1)

    # Assertions
    assert len(chunks) > 0, "Should create at least one chunk"

    for chunk in chunks:
        word_count = count_arabic_words(chunk.text)
        assert word_count >= 50, f"Chunk too small: {word_count} words"
        assert word_count <= 250, f"Chunk too large: {word_count} words"
        assert chunk.chunk_id, "Chunk should have ID"
        assert chunk.page_start == 1, "Page number should be 1"

    print(f"✓ Created {len(chunks)} chunks")
    print(f"✓ Average chunk size: {sum(count_arabic_words(c.text) for c in chunks) / len(chunks):.0f} words")
    print("✓ All chunking tests passed")

if __name__ == "__main__":
    test_chunking()
