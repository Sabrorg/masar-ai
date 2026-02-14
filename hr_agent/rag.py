"""
RAG (Retrieval-Augmented Generation) module
"""
from typing import Optional, List, Dict, Any
from hr_agent.vectordb import VectorDB
from hr_agent.db import EmployeeDB
from hr_agent.routing import QueryRouter
from hr_agent.llm import LLM
from hr_agent.schemas import RetrievedChunk
from hr_agent.utils import format_employee_info, get_logger

logger = get_logger(__name__)

class RAGSystem:
    """
    Complete RAG system for HR Assistant
    """

    def __init__(
        self,
        vectordb: VectorDB,
        employee_db: EmployeeDB,
        router: QueryRouter,
        llm: Optional[LLM] = None,
        top_k: int = 6
    ):
        self.vectordb = vectordb
        self.employee_db = employee_db
        self.router = router
        self.llm = llm
        self.top_k = top_k

    def answer_query(
        self,
        query: str,
        employee_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer a query using appropriate data sources

        Returns:
            {
                "answer": str,
                "route": str,
                "retrieved_chunks": List[RetrievedChunk],
                "employee_data": Optional[dict],
                "citations": List[str]
            }
        """
        # Route query
        route_decision = self.router.route(query)
        route_type = route_decision.route_type

        logger.info(f"Processing query (route={route_type}): {query[:50]}...")

        # Initialize response components
        retrieved_chunks = []
        employee_data = None
        citations = []

        # Fetch employee data if needed
        if route_type in ["db", "hybrid"] and employee_id:
            employee = self.employee_db.get_employee(employee_id)
            if employee:
                employee_data = {
                    "employee_id": employee.employee_id,
                    "full_name_ar": employee.full_name_ar,
                    "department": employee.department,
                    "job_title_ar": employee.job_title_ar,
                    "grade_level": employee.grade_level,
                    "base_salary_sar": employee.base_salary_sar,
                    "allowances_sar": employee.allowances_sar,
                    "total_salary_sar": employee.total_salary_sar,
                    "performance_rating_year": employee.performance_rating_year,
                    "performance_notes_ar": employee.performance_notes_ar,
                    "yearly_goal_title_ar": employee.yearly_goal_title_ar,
                    "yearly_goal_kpis_ar": employee.yearly_goal_kpis_ar,
                    "training_plan_ar": employee.training_plan_ar,
                    "last_month_deductions_sar": employee.last_month_deductions_sar,
                    "warnings_count": employee.warnings_count,
                }

        # Retrieve policy chunks if needed
        if route_type in ["rag", "hybrid"]:
            retrieved_chunks = self.vectordb.search(query, top_k=self.top_k)
            citations = [chunk.citation() for chunk in retrieved_chunks]

        # Generate answer
        if self.llm and self.llm.available:
            answer = self._generate_llm_answer(
                query, route_type, retrieved_chunks, employee_data
            )
        else:
            answer = self._generate_template_answer(
                query, route_type, retrieved_chunks, employee_data
            )

        return {
            "answer": answer,
            "route": route_type,
            "retrieved_chunks": retrieved_chunks,
            "employee_data": employee_data,
            "citations": citations
        }

    def _generate_llm_answer(
        self,
        query: str,
        route_type: str,
        retrieved_chunks: List[RetrievedChunk],
        employee_data: Optional[Dict]
    ) -> str:
        """Generate answer using LLM"""
        # Build system prompt
        system_prompt = """أنت مساعد موارد بشرية متخصص في نظام العمل السعودي.
مهمتك الإجابة على أسئلة الموظفين بدقة واحترافية.

القواعد المهمة:
1. استخدم فقط المعلومات المتوفرة في السياق المقدم
2. لا تخترع معلومات أو قوانين غير موجودة
3. إذا لم تكن المعلومات كافية، اذكر ذلك بوضوح
4. اذكر مصادر المعلومات (أرقام الصفحات) عند الاستناد إلى اللائحة
5. كن مهذباً ومساعداً"""

        # Build user prompt based on route type
        user_prompt = f"السؤال: {query}\n\n"

        if route_type == "db" and employee_data:
            user_prompt += "بيانات الموظف:\n"
            user_prompt += f"- الاسم: {employee_data['full_name_ar']}\n"
            user_prompt += f"- الرقم الوظيفي: {employee_data['employee_id']}\n"
            user_prompt += f"- القسم: {employee_data['department']}\n"
            user_prompt += f"- المسمى الوظيفي: {employee_data['job_title_ar']}\n"
            user_prompt += f"- الراتب الأساسي: {employee_data['base_salary_sar']:,.2f} ريال\n"
            user_prompt += f"- البدلات: {employee_data['allowances_sar']:,.2f} ريال\n"
            user_prompt += f"- إجمالي الراتب: {employee_data['total_salary_sar']:,.2f} ريال\n"
            user_prompt += f"- التقييم السنوي: {employee_data['performance_rating_year']}/5\n"
            user_prompt += f"- ملاحظات الأداء: {employee_data['performance_notes_ar']}\n"
            user_prompt += f"- الهدف السنوي: {employee_data['yearly_goal_title_ar']}\n"
            user_prompt += f"- مؤشرات الأداء: {employee_data['yearly_goal_kpis_ar']}\n"
            if employee_data['last_month_deductions_sar'] > 0:
                user_prompt += f"- الخصومات الشهر الماضي: {employee_data['last_month_deductions_sar']:,.2f} ريال\n"

        elif route_type == "rag" and retrieved_chunks:
            user_prompt += "مقتطفات من اللائحة التنفيذية لنظام العمل:\n\n"
            for i, chunk in enumerate(retrieved_chunks, 1):
                user_prompt += f"[مقتطف {i}] (صفحة {chunk.page_start}):\n{chunk.text}\n\n"

        elif route_type == "hybrid":
            if employee_data:
                user_prompt += "بيانات الموظف:\n"
                user_prompt += f"- الاسم: {employee_data['full_name_ar']}\n"
                user_prompt += f"- الراتب الإجمالي: {employee_data['total_salary_sar']:,.2f} ريال\n"
                user_prompt += f"- الخصومات الشهر الماضي: {employee_data['last_month_deductions_sar']:,.2f} ريال\n"
                user_prompt += f"- عدد الإنذارات: {employee_data['warnings_count']}\n\n"

            if retrieved_chunks:
                user_prompt += "مقتطفات من اللائحة التنفيذية:\n\n"
                for i, chunk in enumerate(retrieved_chunks, 1):
                    user_prompt += f"[مقتطف {i}] (صفحة {chunk.page_start}):\n{chunk.text}\n\n"

        user_prompt += "\nالرجاء تقديم إجابة واضحة ومفيدة مع ذكر المصادر."

        # Generate answer
        answer = self.llm.generate_answer(system_prompt, user_prompt)

        # Add citations if not already included
        if retrieved_chunks and "صفحة" not in answer:
            answer += "\n\nالمصادر:\n"
            for chunk in retrieved_chunks:
                answer += f"- {chunk.citation()}\n"

        return answer

    def _generate_template_answer(
        self,
        query: str,
        route_type: str,
        retrieved_chunks: List[RetrievedChunk],
        employee_data: Optional[Dict]
    ) -> str:
        """Generate template-based answer (fallback when LLM unavailable)"""
        answer_parts = []

        if route_type == "db" and employee_data:
            answer_parts.append("معلومات الموظف:\n")
            answer_parts.append(f"الاسم: {employee_data['full_name_ar']}")
            answer_parts.append(f"الرقم الوظيفي: {employee_data['employee_id']}")
            answer_parts.append(f"القسم: {employee_data['department']}")
            answer_parts.append(f"المسمى الوظيفي: {employee_data['job_title_ar']}")
            answer_parts.append(f"الراتب الأساسي: {employee_data['base_salary_sar']:,.2f} ريال")
            answer_parts.append(f"البدلات: {employee_data['allowances_sar']:,.2f} ريال")
            answer_parts.append(f"إجمالي الراتب: {employee_data['total_salary_sar']:,.2f} ريال")
            answer_parts.append(f"التقييم السنوي: {employee_data['performance_rating_year']}/5")
            answer_parts.append(f"الهدف السنوي: {employee_data['yearly_goal_title_ar']}")

        elif route_type == "rag" and retrieved_chunks:
            answer_parts.append("المعلومات من اللائحة التنفيذية لنظام العمل:\n")
            for i, chunk in enumerate(retrieved_chunks[:3], 1):  # Show top 3
                answer_parts.append(f"\n[{i}] {chunk.text[:300]}...")
                answer_parts.append(f"    المصدر: {chunk.citation()}")

        elif route_type == "hybrid":
            if employee_data:
                answer_parts.append("بياناتك الشخصية:")
                answer_parts.append(f"- الراتب الإجمالي: {employee_data['total_salary_sar']:,.2f} ريال")
                if employee_data['last_month_deductions_sar'] > 0:
                    answer_parts.append(f"- الخصومات الشهر الماضي: {employee_data['last_month_deductions_sar']:,.2f} ريال")
                answer_parts.append("")

            if retrieved_chunks:
                answer_parts.append("من اللائحة:")
                for chunk in retrieved_chunks[:2]:
                    answer_parts.append(f"- {chunk.text[:200]}...")
                    answer_parts.append(f"  المصدر: {chunk.citation()}")

        if not answer_parts:
            answer_parts.append("عذراً، لم أتمكن من العثور على معلومات كافية للإجابة على سؤالك.")

        answer_parts.append("\n[ملاحظة: نموذج اللغة غير متوفر. النتائج من البحث المباشر فقط]")

        return "\n".join(answer_parts)

def create_rag_system(
    vectordb: VectorDB,
    employee_db: EmployeeDB,
    router: QueryRouter,
    llm: Optional[LLM] = None,
    top_k: int = 6
) -> RAGSystem:
    """Factory function to create RAG system"""
    return RAGSystem(vectordb, employee_db, router, llm, top_k)
