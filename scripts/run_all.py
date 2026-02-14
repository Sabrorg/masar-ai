#!/usr/bin/env python3
"""
Main runner script - executes all setup steps
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from hr_agent.utils import get_logger
import subprocess

logger = get_logger(__name__)

def run_script(script_name: str, description: str) -> bool:
    """Run a script and return success status"""
    print("\n" + "=" * 60)
    print(f"Running: {description}")
    print("=" * 60)

    script_path = Path(__file__).parent / script_name
    result = subprocess.run([sys.executable, str(script_path)])

    if result.returncode == 0:
        logger.info(f"✓ {description} completed successfully")
        return True
    else:
        logger.error(f"✗ {description} failed")
        return False

def main():
    """Run all setup steps"""
    print("=" * 70)
    print(" HR ASSISTANT DEMO - COMPLETE SETUP")
    print("=" * 70)

    # Print configuration
    config.print_config()

    # Ensure storage directories exist
    logger.info("Creating storage directories...")
    config.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    config.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("✓ Storage directories ready")

    success_count = 0
    total_steps = 3

    # Step 1: Build employee database
    if config.SQLITE_PATH.exists():
        logger.info(f"Employee database already exists at: {config.SQLITE_PATH}")
        response = input("Rebuild employee database? (yes/no) [no]: ").strip().lower()
        if response != "yes":
            logger.info("Skipping database build")
            success_count += 1
        else:
            if run_script("build_employee_db.py", "Employee Database Build"):
                success_count += 1
    else:
        if run_script("build_employee_db.py", "Employee Database Build"):
            success_count += 1

    # Step 2: Ingest PDF and build vector index
    from hr_agent.vectordb import create_vectordb

    try:
        # Check if index exists
        vectordb = create_vectordb(
            config.CHROMA_DIR,
            config.CHROMA_COLLECTION_NAME,
            None  # No embedding model for quick check
        )
        chunk_count = vectordb.count()

        if chunk_count > 0:
            logger.info(f"Vector index already exists with {chunk_count} chunks")
            response = input("Rebuild vector index? (yes/no) [no]: ").strip().lower()
            if response != "yes":
                logger.info("Skipping PDF ingestion")
                success_count += 1
            else:
                if run_script("ingest_pdf.py", "PDF Ingestion & Vector Index Build"):
                    success_count += 1
        else:
            if run_script("ingest_pdf.py", "PDF Ingestion & Vector Index Build"):
                success_count += 1
    except Exception as e:
        logger.warning(f"Could not check vector index: {e}")
        if run_script("ingest_pdf.py", "PDF Ingestion & Vector Index Build"):
            success_count += 1

    # Step 3: Run sanity demo
    if run_script("sanity_demo.py", "Sanity Check Demo"):
        success_count += 1

    # Final summary
    print("\n" + "=" * 70)
    print(" SETUP SUMMARY")
    print("=" * 70)
    print(f"Completed: {success_count}/{total_steps} steps")

    if success_count == total_steps:
        print("\n✓ ALL STEPS COMPLETED SUCCESSFULLY!")
        print("\nNext steps:")
        print("  1. Ensure models are downloaded and paths are correct in config.py")
        print("  2. Run the Streamlit app:")
        print("     streamlit run app/app.py")
    else:
        print("\n⚠️  SOME STEPS FAILED")
        print("Please check the errors above and fix any issues.")

    print("=" * 70)

    return 0 if success_count == total_steps else 1

if __name__ == "__main__":
    sys.exit(main())
