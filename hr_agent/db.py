"""
Employee database module using SQLite
"""
from typing import Optional, List
from pathlib import Path
from datetime import datetime, timedelta, date
import random
from sqlalchemy import create_engine, Column, String, Integer, Float, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from faker import Faker
from hr_agent.utils import get_logger

logger = get_logger(__name__)

Base = declarative_base()

class EmployeeModel(Base):
    """SQLAlchemy model for employees"""
    __tablename__ = 'employees'

    employee_id = Column(String, primary_key=True)
    full_name_ar = Column(String, nullable=False)
    department = Column(String, nullable=False)
    job_title_ar = Column(String, nullable=False)
    grade_level = Column(Integer, nullable=False)
    manager_id = Column(String, nullable=True)
    hire_date = Column(Date, nullable=False)
    base_salary_sar = Column(Float, nullable=False)
    allowances_sar = Column(Float, nullable=False)
    total_salary_sar = Column(Float, nullable=False)
    performance_rating_year = Column(Integer, nullable=False)
    performance_notes_ar = Column(Text, nullable=False)
    yearly_goal_title_ar = Column(Text, nullable=False)
    yearly_goal_kpis_ar = Column(Text, nullable=False)
    training_plan_ar = Column(Text, nullable=False)
    last_promotion_date = Column(Date, nullable=True)
    warnings_count = Column(Integer, default=0)
    last_month_deductions_sar = Column(Float, default=0.0)

class EmployeeDB:
    """Employee database manager"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    def get_employee(self, employee_id: str) -> Optional[EmployeeModel]:
        """Get employee by ID"""
        session = self.get_session()
        try:
            return session.query(EmployeeModel).filter_by(employee_id=employee_id).first()
        finally:
            session.close()

    def search_employee_by_name(self, name_partial: str) -> List[EmployeeModel]:
        """Search employees by partial name"""
        session = self.get_session()
        try:
            return session.query(EmployeeModel).filter(
                EmployeeModel.full_name_ar.like(f'%{name_partial}%')
            ).limit(10).all()
        finally:
            session.close()

    def get_all_employees(self, limit: Optional[int] = None) -> List[EmployeeModel]:
        """Get all employees"""
        session = self.get_session()
        try:
            query = session.query(EmployeeModel)
            if limit:
                query = query.limit(limit)
            return query.all()
        finally:
            session.close()

    def count_employees(self) -> int:
        """Count total employees"""
        session = self.get_session()
        try:
            return session.query(EmployeeModel).count()
        finally:
            session.close()

    def update_goal(self, employee_id: str, new_goal_title: str, new_goal_kpis: str) -> bool:
        """Update employee goal"""
        session = self.get_session()
        try:
            employee = session.query(EmployeeModel).filter_by(employee_id=employee_id).first()
            if employee:
                employee.yearly_goal_title_ar = new_goal_title
                employee.yearly_goal_kpis_ar = new_goal_kpis
                session.commit()
                return True
            return False
        finally:
            session.close()

def generate_synthetic_employees(db: EmployeeDB, count: int = 1000, seed: int = 42):
    """
    Generate synthetic employee data with Arabic names
    """
    random.seed(seed)

    # Try Arabic locales
    fake = None
    for locale in ['ar_SA', 'ar_EG', 'ar']:
        try:
            fake = Faker(locale)
            break
        except:
            continue

    if fake is None:
        logger.warning("Arabic locale not available, using default")
        fake = Faker()

    Faker.seed(seed)

    departments = [
        "الموارد البشرية",
        "المالية",
        "تقنية المعلومات",
        "المبيعات",
        "العمليات",
        "الشؤون القانونية",
        "التسويق",
        "خدمة العملاء",
        "الإنتاج",
        "الجودة"
    ]

    job_titles = [
        "مدير",
        "مدير عام",
        "نائب مدير",
        "رئيس قسم",
        "مشرف",
        "أخصائي أول",
        "أخصائي",
        "محلل بيانات",
        "مهندس برمجيات",
        "أخصائي موارد بشرية",
        "محاسب",
        "مسؤول مبيعات",
        "منسق",
        "مساعد إداري"
    ]

    performance_notes = [
        "أداء ممتاز ويتجاوز التوقعات",
        "أداء جيد جداً ويحقق الأهداف بكفاءة",
        "أداء جيد ويلبي المتطلبات",
        "أداء مقبول ويحتاج تحسين في بعض المجالات",
        "أداء يحتاج تطوير ومتابعة"
    ]

    goal_titles = [
        "تحسين الإنتاجية بنسبة 15%",
        "تطوير نظام إدارة جديد",
        "زيادة رضا العملاء",
        "تقليل التكاليف التشغيلية",
        "تطوير مهارات الفريق",
        "إطلاق منتجات جديدة",
        "تحسين جودة العمليات"
    ]

    kpis = [
        "إنجاز المشاريع في الوقت المحدد",
        "تحقيق نسبة رضا 90%",
        "تقليل الأخطاء بنسبة 20%",
        "زيادة المبيعات بنسبة 10%",
        "تدريب 5 موظفين جدد"
    ]

    training_plans = [
        "• دورة في القيادة الإدارية\n• ورشة عمل في التخطيط الاستراتيجي",
        "• تدريب على البرامج المحاسبية\n• دورة في التحليل المالي",
        "• دورة في البرمجة المتقدمة\n• ورشة عمل في الذكاء الاصطناعي",
        "• دورة في خدمة العملاء\n• تدريب على مهارات التواصل",
        "• ورشة عمل في إدارة الوقت\n• دورة في حل المشكلات"
    ]

    employees = []
    session = db.get_session()

    try:
        logger.info(f"Generating {count} synthetic employees...")

        for i in range(1, count + 1):
            # Generate employee ID
            employee_id = f"E{i:04d}"

            # Generate Arabic name (or fallback)
            try:
                full_name_ar = fake.name()
            except:
                full_name_ar = f"موظف {i}"

            # Department and job title
            department = random.choice(departments)
            job_title_ar = random.choice(job_titles)

            # Grade level (1-10, weighted toward middle)
            grade_level = random.choices(range(1, 11), weights=[5, 8, 12, 15, 20, 20, 15, 10, 5, 2])[0]

            # Manager (pick from earlier employees with higher grade)
            manager_id = None
            if i > 10 and random.random() > 0.1:  # 90% have managers
                potential_managers = [j for j in range(max(1, i - 50), i) if (j % 10 <= grade_level)]
                if potential_managers:
                    manager_id = f"E{random.choice(potential_managers):04d}"

            # Hire date (random date in last 10 years)
            days_ago = random.randint(0, 3650)
            hire_date = datetime.now().date() - timedelta(days=days_ago)

            # Salary based on grade
            base_salary_sar = random.uniform(4000, 8000) + (grade_level * 1500)
            allowances_sar = random.uniform(1000, 3000) + (grade_level * 200)
            total_salary_sar = base_salary_sar + allowances_sar

            # Performance rating (1-5, weighted toward good)
            performance_rating = random.choices([1, 2, 3, 4, 5], weights=[2, 8, 25, 40, 25])[0]
            performance_notes_ar = performance_notes[performance_rating - 1]

            # Goals and KPIs
            yearly_goal_title_ar = random.choice(goal_titles)
            yearly_goal_kpis_ar = random.choice(kpis)

            # Training plan
            training_plan_ar = random.choice(training_plans)

            # Last promotion (maybe)
            last_promotion_date = None
            if random.random() > 0.6 and days_ago > 365:
                promo_days_ago = random.randint(180, days_ago - 180)
                last_promotion_date = datetime.now().date() - timedelta(days=promo_days_ago)

            # Warnings (mostly 0)
            warnings_count = random.choices([0, 1, 2, 3], weights=[85, 10, 4, 1])[0]

            # Last month deductions (mostly 0)
            if warnings_count > 0 or random.random() < 0.1:
                last_month_deductions_sar = random.uniform(100, 500)
            else:
                last_month_deductions_sar = 0.0

            employee = EmployeeModel(
                employee_id=employee_id,
                full_name_ar=full_name_ar,
                department=department,
                job_title_ar=job_title_ar,
                grade_level=grade_level,
                manager_id=manager_id,
                hire_date=hire_date,
                base_salary_sar=round(base_salary_sar, 2),
                allowances_sar=round(allowances_sar, 2),
                total_salary_sar=round(total_salary_sar, 2),
                performance_rating_year=performance_rating,
                performance_notes_ar=performance_notes_ar,
                yearly_goal_title_ar=yearly_goal_title_ar,
                yearly_goal_kpis_ar=yearly_goal_kpis_ar,
                training_plan_ar=training_plan_ar,
                last_promotion_date=last_promotion_date,
                warnings_count=warnings_count,
                last_month_deductions_sar=round(last_month_deductions_sar, 2)
            )
            employees.append(employee)

            # Batch insert every 100 employees
            if len(employees) >= 100:
                session.add_all(employees)
                session.commit()
                logger.info(f"  Generated {i}/{count} employees...")
                employees = []

        # Insert remaining
        if employees:
            session.add_all(employees)
            session.commit()

        logger.info(f"✓ Generated {count} synthetic employees")

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to generate employees: {e}")
        raise
    finally:
        session.close()

def create_employee_db(db_path: Path) -> EmployeeDB:
    """Factory function to create employee database"""
    return EmployeeDB(db_path)
