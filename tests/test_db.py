"""
Test employee database functionality
"""
import sys
from pathlib import Path
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hr_agent.db import create_employee_db, generate_synthetic_employees

def test_employee_db():
    """Test employee database"""
    print("Testing employee database...")

    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    try:
        # Create database
        db = create_employee_db(db_path)

        # Generate employees
        count = 100
        generate_synthetic_employees(db, count=count, seed=42)

        # Check count
        actual_count = db.count_employees()
        assert actual_count == count, f"Expected {count} employees, got {actual_count}"
        print(f"✓ Generated {actual_count} employees")

        # Check employee IDs
        employees = db.get_all_employees()
        employee_ids = [emp.employee_id for emp in employees]
        assert len(set(employee_ids)) == count, "Employee IDs should be unique"
        print("✓ All employee IDs are unique")

        # Check first employee
        first_emp = db.get_employee("E0001")
        assert first_emp is not None, "Should find first employee"
        assert first_emp.employee_id == "E0001"
        assert first_emp.full_name_ar, "Should have Arabic name"
        assert first_emp.total_salary_sar > 0, "Should have salary"
        print(f"✓ Sample employee: {first_emp.full_name_ar} - {first_emp.job_title_ar}")

        # Check salary ranges
        salaries = [emp.total_salary_sar for emp in employees]
        min_salary = min(salaries)
        max_salary = max(salaries)
        assert min_salary > 0, "All salaries should be positive"
        assert max_salary > min_salary, "Should have salary range"
        print(f"✓ Salary range: {min_salary:,.0f} - {max_salary:,.0f} SAR")

        # Check departments
        departments = set(emp.department for emp in employees)
        assert len(departments) > 1, "Should have multiple departments"
        print(f"✓ {len(departments)} departments created")

        print("✓ All database tests passed")

    finally:
        # Cleanup
        if db_path.exists():
            db_path.unlink()

if __name__ == "__main__":
    test_employee_db()
