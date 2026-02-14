#!/usr/bin/env python3
"""
Streamlit app for HR Assistant Demo
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import config
from hr_agent.db import create_employee_db, generate_synthetic_employees
from hr_agent.embeddings import create_embedding_model
from hr_agent.vectordb import create_vectordb
from hr_agent.routing import create_router
from hr_agent.llm import create_llm
from hr_agent.rag import create_rag_system
from hr_agent.pdf_ingest import extract_pdf
from hr_agent.chunking import create_chunker
import subprocess
import time

# Page configuration
st.set_page_config(
    page_title="مساعد الموارد البشرية",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for RTL support and better styling
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        direction: rtl;
        text-align: right;
    }
    .stSelectbox > div > div > select {
        direction: rtl;
        text-align: right;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        direction: rtl;
        text-align: right;

        /* dark-mode friendly */
        color: #eaeaea !important;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
    }

    .user-message {
        background: rgba(59, 130, 246, 0.18) !important;   /* blue tint */
    }

    .assistant-message {
        background: rgba(255, 255, 255, 0.06) !important;  /* subtle gray */
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def initialize_system():
    """Initialize all system components (cached)"""
    try:
        # Database
        db = create_employee_db(config.SQLITE_PATH)

        # Embedding model (if available)
        embedding_model = None
        if config.EMBED_MODEL_PATH.exists():
            embedding_model = create_embedding_model(config.EMBED_MODEL_PATH)
        else:
            st.warning(f"⚠️ Embedding model not found at: {config.EMBED_MODEL_PATH}")

        # Vector database
        vectordb = create_vectordb(
            config.CHROMA_DIR,
            config.CHROMA_COLLECTION_NAME,
            embedding_model
        )

        # Router
        router = create_router()

        # LLM (if available)
        llm = None
        if config.LLM_MODEL_PATH.exists():
            llm = create_llm(config.LLM_MODEL_PATH, use_4bit=False)
        else:
            st.warning(f"⚠️ LLM model not found at: {config.LLM_MODEL_PATH}")
            st.info("ℹ️ App running in retrieval-only mode")

        # RAG system
        rag_system = create_rag_system(
            vectordb=vectordb,
            employee_db=db,
            router=router,
            llm=llm,
            top_k=config.TOP_K
        )

        return {
            "db": db,
            "vectordb": vectordb,
            "rag_system": rag_system,
            "llm_available": llm.available if llm else False
        }

    except Exception as e:
        st.error(f"❌ Failed to initialize system: {e}")
        return None

def rebuild_employee_db():
    """Rebuild employee database"""
    with st.spinner("جاري بناء قاعدة بيانات الموظفين..."):
        try:
            db = create_employee_db(config.SQLITE_PATH)

            # Clear existing
            session = db.get_session()
            from hr_agent.db import EmployeeModel
            session.query(EmployeeModel).delete()
            session.commit()
            session.close()

            # Generate new
            generate_synthetic_employees(db, count=config.EMPLOYEE_COUNT, seed=config.RANDOM_SEED)

            st.success(f"✓ تم إنشاء {config.EMPLOYEE_COUNT} موظف")
            st.cache_resource.clear()
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"❌ فشل بناء قاعدة البيانات: {e}")

def rebuild_vector_index():
    """Rebuild vector index"""
    with st.spinner("جاري بناء فهرس البحث..."):
        try:
            # Check PDF
            if not config.PDF_PATH.exists():
                st.error(f"❌ ملف PDF غير موجود: {config.PDF_PATH}")
                return

            # Check embedding model
            if not config.EMBED_MODEL_PATH.exists():
                st.error(f"❌ نموذج التضمين غير موجود: {config.EMBED_MODEL_PATH}")
                return

            # Extract PDF
            pages = extract_pdf(config.PDF_PATH)
            st.info(f"📄 تم استخراج {len(pages)} صفحة")

            # Chunk
            chunker = create_chunker(
                min_words=config.CHUNK_MIN_WORDS,
                max_words=config.CHUNK_MAX_WORDS,
                overlap_words=config.CHUNK_OVERLAP_WORDS
            )
            chunks = chunker.chunk_pages(pages)
            st.info(f"✂️ تم إنشاء {len(chunks)} قطعة نصية")

            # Load embedding model
            embedding_model = create_embedding_model(config.EMBED_MODEL_PATH)

            # Create vectordb
            vectordb = create_vectordb(
                config.CHROMA_DIR,
                config.CHROMA_COLLECTION_NAME,
                embedding_model
            )

            # Reset and add
            vectordb.reset()
            vectordb.add_chunks(chunks, show_progress=False)

            st.success(f"✓ تم بناء الفهرس بنجاح ({len(chunks)} قطعة)")
            st.cache_resource.clear()
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"❌ فشل بناء الفهرس: {e}")

def main():
    """Main Streamlit app"""

    # Sidebar
    st.sidebar.title("⚙️ الإعدادات")

    # System status
    st.sidebar.subheader("حالة النظام")

    system = initialize_system()

    if system:
        emp_count = system["db"].count_employees()
        chunk_count = system["vectordb"].count()
        llm_status = "✓ متوفر" if system["llm_available"] else "⚠️ غير متوفر"

        st.sidebar.success(f"قاعدة الموظفين: {emp_count} موظف")
        st.sidebar.success(f"فهرس البحث: {chunk_count} قطعة")
        st.sidebar.info(f"نموذج اللغة: {llm_status}")
    else:
        st.sidebar.error("❌ فشل تحميل النظام")
        st.stop()

    # Employee selector
    st.sidebar.subheader("اختر موظف")

    all_employees = system["db"].get_all_employees(limit=100)
    employee_options = {
        f"{emp.employee_id} - {emp.full_name_ar}": emp.employee_id
        for emp in all_employees
    }

    if employee_options:
        selected_label = st.sidebar.selectbox(
            "الموظف:",
            options=list(employee_options.keys()),
            key="employee_selector"
        )
        selected_employee_id = employee_options[selected_label]
    else:
        st.sidebar.warning("⚠️ لا يوجد موظفون في قاعدة البيانات")
        selected_employee_id = None

    # Management buttons
    st.sidebar.subheader("إدارة البيانات")

    if st.sidebar.button("🔄 إعادة بناء قاعدة الموظفين", use_container_width=True):
        rebuild_employee_db()

    if st.sidebar.button("🔄 إعادة بناء فهرس البحث", use_container_width=True):
        rebuild_vector_index()

    # Main area
    st.title(" مساعد الموارد البشرية")
    st.markdown("مساعدك الذكي للإجابة على أسئلة الموارد البشرية وسياسات العمل في السعودية")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 أنت: {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">🤖 المساعد: {message["content"]}</div>', unsafe_allow_html=True)

                # Show debug info if available
                if "debug" in message and message["debug"]:
                    with st.expander("🔍 تفاصيل تقنية"):
                        debug = message["debug"]
                        st.write(f"**نوع الاستعلام:** {debug['route']}")

                        if debug.get('employee_data'):
                            st.write("**بيانات الموظف المستخدمة:**")
                            st.json(debug['employee_data'])

                        if debug.get('retrieved_chunks'):
                            st.write(f"**عدد القطع المسترجعة:** {len(debug['retrieved_chunks'])}")
                            for i, chunk in enumerate(debug['retrieved_chunks'][:3], 1):
                                st.write(f"**قطعة {i}:**")
                                st.write(f"- النص: {chunk.text[:200]}...")
                                st.write(f"- الصفحة: {chunk.page_start}")
                                st.write(f"- المعرف: {chunk.chunk_id}")

                        if debug.get('citations'):
                            st.write("**المصادر:**")
                            for citation in debug['citations']:
                                st.write(f"- {citation}")

    # Chat input
    user_query = st.chat_input("اكتب سؤالك هنا...")

    if user_query:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_query})

        # Generate response
        with st.spinner("جاري البحث والإجابة..."):
            try:
                result = system["rag_system"].answer_query(
                    query=user_query,
                    employee_id=selected_employee_id
                )

                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "debug": {
                        "route": result["route"],
                        "employee_data": result.get("employee_data"),
                        "retrieved_chunks": result.get("retrieved_chunks"),
                        "citations": result.get("citations")
                    }
                })

            except Exception as e:
                error_msg = f"❌ حدث خطأ: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "debug": None
                })

        # Rerun to show new messages
        st.rerun()

    # Sample queries
    if len(st.session_state.messages) == 0:
        st.subheader("أمثلة على الأسئلة:")
        st.markdown("""
        **أسئلة عن بياناتك الشخصية:**
        - كم راتبي الحالي؟
        - وش تقييمي السنوي؟
        - وش هدفي الحالي وكيف أتابعه؟

        **أسئلة عن السياسات والقوانين:**
        - كيف أطلب إجازة؟ وش حقوقي؟
        - هل يحق للشركة خصم راتبي؟
        - ما هي ساعات العمل القانونية؟
        - كيف يتم احتساب مكافأة نهاية الخدمة؟

        **أسئلة مختلطة:**
        - هل يحق خصم راتبي بسبب التأخير؟ وكم انخصم مني الشهر الماضي؟
        - وش حقوقي في الإجازة وكم رصيدي الحالي؟
        """)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("HR Assistant Demo v1.0")
    st.sidebar.caption("Powered by RAG + Local LLM")

if __name__ == "__main__":
    main()
