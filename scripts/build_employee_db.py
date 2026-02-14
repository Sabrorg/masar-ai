#!/usr/bin/env python3
"""
Script to build synthetic employee database
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from hr_agent.db import create_employee_db, generate_synthetic_employees
from hr_agent.utils import get_logger

logger = get_logger(__name__)

def main():
    """Build synthetic employee database"""
    print("=" * 60)
    print("EMPLOYEE DATABASE BUILD")
    print("=" * 60)

    try:
        # Create database
        logger.info("Creating employee database...")
        db = create_employee_db(config.SQLITE_PATH)

        # Check if already populated
        existing_count = db.count_employees()
        if existing_count > 0:
            logger.warning(f"Database already has {existing_count} employees")
            response = input("Do you want to rebuild? (yes/no): ").strip().lower()
            if response != "yes":
                logger.info("Keeping existing database")
                return 0

            # Clear existing data
            logger.info("Clearing existing data...")
            session = db.get_session()
            from hr_agent.db import EmployeeModel
            session.query(EmployeeModel).delete()
            session.commit()
            session.close()
            logger.info("Existing data cleared")

        # Generate synthetic employees
        logger.info(f"Generating {config.EMPLOYEE_COUNT} synthetic employees...")
        generate_synthetic_employees(
            db,
            count=config.EMPLOYEE_COUNT,
            seed=config.RANDOM_SEED
        )

        # Verify
        final_count = db.count_employees()
        logger.info(f"✓ Final employee count: {final_count}")

        # Show sample employees
        logger.info("Sample employees:")
        samples = db.get_all_employees(limit=5)
        for emp in samples:
            logger.info(f"  {emp.employee_id}: {emp.full_name_ar} - {emp.job_title_ar}")

        print("\n" + "=" * 60)
        print("DATABASE BUILD COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Total Employees: {final_count}")
        print(f"Database Path:   {config.SQLITE_PATH}")
        print("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"Failed to build database: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
