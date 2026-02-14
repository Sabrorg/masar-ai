"""
Query routing module
Determines whether to route queries to DB, RAG, or both
"""
import re
from hr_agent.schemas import QueryRoute
from hr_agent.utils import get_logger

logger = get_logger(__name__)

class QueryRouter:
    """
    Routes queries to appropriate data sources
    """

    def __init__(self):
        # Keywords for DB queries (employee personal data)
        self.db_keywords = [
            'راتب', 'راتبي', 'بدلات', 'بدلاتي', 'خصوم', 'خصومات', 'خصمت',
            'تقييم', 'تقييمي', 'أداء', 'أدائي',
            'هدف', 'هدفي', 'أهداف', 'أهدافي',
            'تدريب', 'تدريبي', 'دورات',
            'مدير', 'مديري',
            'معلومات', 'معلوماتي', 'بيانات', 'بياناتي',
            'قسم', 'قسمي', 'إدارة', 'إدارتي',
            'وظيفة', 'وظيفتي', 'مسمى',
            'ترقية', 'ترقيتي',
            'إنذار', 'إنذارات', 'مخالفات'
        ]

        # Keywords for RAG queries (policy/legal)
        self.rag_keywords = [
            'حق', 'حقوق', 'حقي', 'يحق',
            'إجازة', 'إجازات',
            'نظام', 'قانون', 'لائحة',
            'فصل', 'إنهاء', 'استقالة',
            'ساعات عمل', 'دوام', 'عمل إضافي', 'عمل إضافية',
            'فترة تجربة', 'تجريبية',
            'عقد', 'عقود',
            'مكافأة', 'نهاية خدمة', 'نهاية الخدمة',
            'تعويض',
            'مخالفة', 'عقوبة', 'جزاء',
            'حماية', 'سلامة',
            'تأمينات', 'ضمان'
        ]

    def route(self, query: str) -> QueryRoute:
        """
        Route query to appropriate data source
        """
        query_lower = query.lower()

        # Count keyword matches
        db_score = sum(1 for kw in self.db_keywords if kw in query_lower)
        rag_score = sum(1 for kw in self.rag_keywords if kw in query_lower)

        # Determine route
        if db_score > 0 and rag_score > 0:
            # Hybrid query
            route_type = "hybrid"
            confidence = 0.9
            reasoning = f"Query contains both personal data keywords ({db_score}) and policy keywords ({rag_score})"
        elif db_score > rag_score:
            # DB query
            route_type = "db"
            confidence = 0.8 if db_score >= 2 else 0.6
            reasoning = f"Query contains personal data keywords ({db_score})"
        elif rag_score > db_score:
            # RAG query
            route_type = "rag"
            confidence = 0.8 if rag_score >= 2 else 0.6
            reasoning = f"Query contains policy keywords ({rag_score})"
        else:
            # Default to RAG for general questions
            route_type = "rag"
            confidence = 0.5
            reasoning = "Default to policy search (no strong keyword matches)"

        logger.info(f"Route: {route_type} (confidence={confidence:.2f})")
        return QueryRoute(
            route_type=route_type,
            confidence=confidence,
            reasoning=reasoning
        )

def create_router() -> QueryRouter:
    """Factory function to create query router"""
    return QueryRouter()
