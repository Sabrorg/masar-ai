#!/usr/bin/env python3
"""
Sanity check demo to verify all components work
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from hr_agent.db import create_employee_db
from hr_agent.embeddings import create_embedding_model
from hr_agent.vectordb import create_vectordb
from hr_agent.routing import create_router
from hr_agent.llm import create_llm
from hr_agent.rag import create_rag_system
from hr_agent.utils import get_logger

logger = get_logger(__name__)

def main():
    """Run sanity checks"""
    print("=" * 60)
    print("SANITY CHECK DEMO")
    print("=" * 60)

    try:
        # Check 1: Database
        print("\n[1] Testing Employee Database...")
        db = create_employee_db(config.SQLITE_PATH)
        emp_count = db.count_employees()
        print(f"    ✓ Employee count: {emp_count}")

        if emp_count > 0:
            sample_emp = db.get_employee("E0001")
            if sample_emp:
                print(f"    ✓ Sample employee: {sample_emp.full_name_ar}")
            else:
                print("    ⚠ Could not fetch sample employee")
        else:
            print("    ⚠ No employees in database. Run build_employee_db.py first.")

        # Check 2: Vector Database
        print("\n[2] Testing Vector Database...")
        if config.EMBED_MODEL_PATH.exists():
            embedding_model = create_embedding_model(config.EMBED_MODEL_PATH)
            vectordb = create_vectordb(
                config.CHROMA_DIR,
                config.CHROMA_COLLECTION_NAME,
                embedding_model
            )
            chunk_count = vectordb.count()
            print(f"    ✓ Chunk count: {chunk_count}")

            if chunk_count > 0:
                # Test retrieval
                test_query = "ما هي حقوق الموظف في الإجازات؟"
                results = vectordb.search(test_query, top_k=2)
                print(f"    ✓ Retrieved {len(results)} chunks for test query")
                if results:
                    print(f"    ✓ Top result: {results[0].text[:100]}...")
            else:
                print("    ⚠ No chunks in vector database. Run ingest_pdf.py first.")
        else:
            print(f"    ⚠ Embedding model not found at: {config.EMBED_MODEL_PATH}")

        # Check 3: Routing
        print("\n[3] Testing Query Router...")
        router = create_router()
        test_queries = [
            ("كم راتبي الحالي؟", "db"),
            ("ما هي حقوق الموظف في الإجازات؟", "rag"),
            ("هل يحق للشركة خصم راتبي بسبب التأخير؟", "hybrid")
        ]
        for query, expected in test_queries:
            route = router.route(query)
            status = "✓" if route.route_type == expected else "⚠"
            print(f"    {status} '{query[:30]}...' -> {route.route_type}")

        # Check 4: LLM (optional)
        print("\n[4] Testing LLM...")
        if config.LLM_MODEL_PATH.exists():
            llm = create_llm(config.LLM_MODEL_PATH, use_4bit=False)
            if llm.available:
                print("    ✓ LLM loaded successfully")
            else:
                print("    ⚠ LLM failed to load")
        else:
            print(f"    ⚠ LLM model not found at: {config.LLM_MODEL_PATH}")
            print("    → App will run in retrieval-only mode")

        # Check 5: End-to-end RAG
        print("\n[5] Testing End-to-End RAG...")
        if emp_count > 0 and chunk_count > 0:
            # Initialize components
            embedding_model = create_embedding_model(config.EMBED_MODEL_PATH) if config.EMBED_MODEL_PATH.exists() else None
            vectordb = create_vectordb(
                config.CHROMA_DIR,
                config.CHROMA_COLLECTION_NAME,
                embedding_model
            )
            llm = create_llm(config.LLM_MODEL_PATH, use_4bit=False) if config.LLM_MODEL_PATH.exists() else None
            router = create_router()

            rag_system = create_rag_system(
                vectordb=vectordb,
                employee_db=db,
                router=router,
                llm=llm,
                top_k=config.TOP_K
            )

            # Test DB query
            print("\n    [5a] Testing DB query...")
            result = rag_system.answer_query(
                "كم راتبي الحالي؟",
                employee_id="E0001"
            )
            print(f"    ✓ Route: {result['route']}")
            print(f"    ✓ Answer: {result['answer'][:150]}...")

            # Test RAG query
            print("\n    [5b] Testing RAG query...")
            result = rag_system.answer_query("ما هي حقوق الموظف في الإجازات؟")
            print(f"    ✓ Route: {result['route']}")
            print(f"    ✓ Retrieved chunks: {len(result['retrieved_chunks'])}")
            print(f"    ✓ Answer: {result['answer'][:150]}...")

        else:
            print("    ⚠ Cannot test RAG: missing data or index")

        print("\n" + "=" * 60)
        print("SANITY CHECK COMPLETED")
        print("=" * 60)

        # Summary
        issues = []
        if emp_count == 0:
            issues.append("No employees in database")
        if chunk_count == 0:
            issues.append("No chunks in vector database")
        if not config.LLM_MODEL_PATH.exists():
            issues.append("LLM model not found (optional)")

        if issues:
            print("\n⚠️  WARNINGS:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✓ All systems operational!")

        return 0

    except Exception as e:
        logger.error(f"Sanity check failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
