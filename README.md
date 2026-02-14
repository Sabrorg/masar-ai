# HR Assistant Demo | مساعد الموارد البشرية

An intelligent HR assistant for Saudi Arabia combining RAG (Retrieval-Augmented Generation) over Saudi labor policies with synthetic employee database queries.

نظام مساعد ذكي للموارد البشرية في السعودية يجمع بين تقنية RAG للوائح العمل السعودية وقاعدة بيانات الموظفين.

---

## Features | المميزات

**English:**
- 🤖 RAG-based question answering over Saudi labor bylaws (Arabic PDF)
- 👥 Synthetic employee database with 1000 employees
- 🔍 Smart query routing (DB / RAG / Hybrid)
- 💬 Interactive Streamlit chat interface
- 🖥️ 100% local/offline (no external API calls)
- 🌍 Full Arabic support with RTL interface
- 📊 Answers grounded in documents with citations

**العربية:**
- 🤖 إجابات ذكية مبنية على اللائحة التنفيذية لنظام العمل السعودي
- 👥 قاعدة بيانات اصطناعية لـ 1000 موظف
- 🔍 توجيه ذكي للاستعلامات (قاعدة بيانات / سياسات / مختلط)
- 💬 واجهة محادثة تفاعلية
- 🖥️ عمل محلي 100% بدون اتصال بالإنترنت
- 🌍 دعم كامل للغة العربية
- 📊 إجابات موثقة بالمصادر وأرقام الصفحات

---

## Architecture | البنية المعمارية

```
┌─────────────────────────────────────────────────────┐
│                   Streamlit UI                       │
│              (Arabic RTL Interface)                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  Query Router   │ (Keyword-based + Optional LLM)
         └─────────────────┘
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
   ┌─────┐    ┌───────┐    ┌──────┐
   │ DB  │    │  RAG  │    │Hybrid│
   └─────┘    └───────┘    └──────┘
      │            │            │
      ▼            ▼            ▼
┌──────────┐ ┌────────────────────┐
│ SQLite   │ │  ChromaDB Vector   │
│Employee  │ │  + Embedding Model │
│Database  │ │  + LLM Generator   │
└──────────┘ └────────────────────┘
```

**Components:**
1. **PDF Ingestion**: Extract & chunk Arabic labor policy PDF
2. **Embedding**: Local BGE-M3 model for semantic search
3. **Vector DB**: ChromaDB for policy document retrieval
4. **Employee DB**: SQLite with 1000 synthetic employees
5. **Routing**: Smart query classification
6. **LLM**: Local Qwen/similar model for answer generation
7. **UI**: Streamlit with Arabic RTL support

---

## Project Structure | هيكل المشروع

```
/home/hr_case/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config.py                          # Configuration (paths, settings)
│
├── hr_agent/                          # Core modules
│   ├── __init__.py
│   ├── schemas.py                     # Data models
│   ├── utils.py                       # Helper functions
│   ├── chunking.py                    # Arabic text chunker
│   ├── pdf_ingest.py                  # PDF extraction
│   ├── embeddings.py                  # Embedding model
│   ├── vectordb.py                    # ChromaDB wrapper
│   ├── db.py                          # Employee database
│   ├── routing.py                     # Query router
│   ├── llm.py                         # LLM wrapper
│   └── rag.py                         # Complete RAG system
│
├── scripts/                           # Setup & utility scripts
│   ├── build_employee_db.py           # Generate synthetic employees
│   ├── ingest_pdf.py                  # Process PDF & build index
│   ├── sanity_demo.py                 # Test all components
│   └── run_all.py                     # Main setup runner
│
├── app/                               # Web application
│   └── app.py                         # Streamlit UI
│
├── tests/                             # Unit tests
│   ├── test_chunking.py
│   └── test_db.py
│
├── storage/                           # Runtime data (created automatically)
│   ├── chroma/                        # Vector database
│   └── hr_demo.sqlite                 # Employee database
│
└── models1/                           # Local models (YOU MUST DOWNLOAD)
    ├── BAAI__bge-m3/                  # Embedding model
    └── Qwen__Qwen3-1.7B/              # LLM model
```

---

## Setup Instructions | تعليمات التثبيت

### Prerequisites | المتطلبات

- Python 3.10+
- Conda (Anaconda/Miniconda)
- CUDA-compatible GPU (optional, falls back to CPU)
- 16GB+ RAM recommended
- ~10GB disk space for models

### Step 1: Environment Setup

The conda environment `exp` should already be created. Activate it:

```bash
conda activate exp
```

### Step 2: Install Dependencies

```bash
cd /home/hr_case
pip install -r requirements.txt
```

**Dependencies installed:**
- PyTorch, Transformers, Accelerate
- PyMuPDF (PDF processing)
- ChromaDB (vector database)
- SQLAlchemy, Faker (employee DB)
- Streamlit (web UI)
- bitsandbytes (optional 4-bit quantization)
- sentence-transformers

### Step 3: Download Models

**CRITICAL:** You must download the models and place them in the correct directories:

#### Embedding Model (Required)
```bash
# Download BAAI/bge-m3 or similar multilingual embedding model
# Place in: /home/hr_case/models1/BAAI__bge-m3/

# Example using Hugging Face CLI:
cd /home/hr_case/models1
git clone https://huggingface.co/BAAI/bge-m3 BAAI__bge-m3
```

#### LLM Model (Required for full functionality)
```bash
# Download Qwen/Qwen3-1.7B or similar small instruct model
# Place in: /home/hr_case/models1/Qwen__Qwen3-1.7B/

# Example:
cd /home/hr_case/models1
git clone https://huggingface.co/Qwen/Qwen3-1.7B Qwen__Qwen3-1.7B
```

**Alternative models:**
- Embedding: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
- LLM: Any small instruct model (Llama-3-8B, Mistral-7B, etc.)

### Step 4: Add Arabic PDF

Place the Saudi labor bylaws PDF at:
```
/home/hr_case/اللائحة التنفيذية لنظام العمل وملحقاتها.pdf
```

If you have a different PDF name or location, update `config.py`:
```python
PDF_PATH = Path("/your/custom/path/to/pdf.pdf")
```

### Step 5: Run Setup

Build employee database and ingest PDF:

```bash
conda activate exp
cd /home/hr_case

# Option A: Run everything automatically
python scripts/run_all.py

# Option B: Run steps individually
python scripts/build_employee_db.py
python scripts/ingest_pdf.py
python scripts/sanity_demo.py
```

**What happens:**
1. Creates 1000 synthetic employees in SQLite
2. Extracts Arabic PDF pages
3. Chunks text (150-220 words, 50-word overlap)
4. Generates embeddings using BGE-M3
5. Stores in ChromaDB vector database
6. Runs sanity checks

---

## Running the Application | تشغيل التطبيق

```bash
conda activate exp
cd /home/hr_case
streamlit run app/app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the App | استخدام التطبيق

1. **Select Employee**: Choose from dropdown in sidebar
2. **Ask Questions**: Type in Arabic or English
3. **View Answers**: Get grounded responses with citations
4. **Debug Mode**: Expand "تفاصيل تقنية" to see retrieved chunks and routing

**Example Questions:**

**Personal Data (DB):**
- كم راتبي الحالي؟
- وش تقييمي السنوي؟
- وش هدفي الحالي؟

**Policy (RAG):**
- كيف أطلب إجازة؟
- ما هي ساعات العمل القانونية؟
- كيف يتم احتساب مكافأة نهاية الخدمة؟

**Hybrid:**
- هل يحق خصم راتبي بسبب التأخير؟ وكم انخصم مني الشهر الماضي؟

---

## Configuration | الإعدادات

Edit [config.py](config.py) to customize:

```python
# Paths
PROJECT_ROOT = "/home/hr_case"
PDF_PATH = PROJECT_ROOT / "اللائحة التنفيذية لنظام العمل وملحقاتها.pdf"
EMBED_MODEL_PATH = PROJECT_ROOT / "models1/BAAI__bge-m3"
LLM_MODEL_PATH = PROJECT_ROOT / "models1/Qwen__Qwen3-1.7B"

# Settings
EMPLOYEE_COUNT = 1000
TOP_K = 6
CHUNK_MIN_WORDS = 150
CHUNK_MAX_WORDS = 220
CHUNK_OVERLAP_WORDS = 50
DEVICE_PREFERENCE = "cuda"  # or "cpu"
```

**Environment Variables:**
You can also override via environment variables:
```bash
export DEVICE_PREFERENCE=cpu
export TOP_K=10
export EMPLOYEE_COUNT=500
```

---

## Troubleshooting | حل المشكلات

### Problem: PDF not found
**Error:** `PDF not found at: /home/hr_case/...`

**Solution:**
1. Ensure PDF is placed at exact path in config
2. Check filename matches (Arabic characters)
3. Or update `PDF_PATH` in config.py

### Problem: Embedding model not found
**Error:** `Embedding model not found at: ...`

**Solution:**
1. Download BAAI/bge-m3 from Hugging Face
2. Place in `models1/BAAI__bge-m3/`
3. Or update `EMBED_MODEL_PATH` in config.py

### Problem: LLM not loading
**Error:** `LLM model not found` or loading fails

**Solution:**
1. App will run in retrieval-only mode (still functional)
2. Download compatible model (Qwen, Llama, etc.)
3. Ensure model is instruct-tuned (chat format)
4. For VRAM issues, set `use_4bit=True` in llm.py

### Problem: GPU not detected
**Symptom:** Falls back to CPU, slow performance

**Solution:**
1. Check: `nvidia-smi` and verify CUDA
2. Check: `python -c "import torch; print(torch.cuda.is_available())"`
3. Install correct PyTorch version: https://pytorch.org/get-started/locally/
4. Set `DEVICE_PREFERENCE=cpu` to disable GPU

### Problem: Arabic text extraction issues
**Symptom:** Garbled or missing Arabic text from PDF

**Solution:**
1. Ensure PyMuPDF is installed (preferred for Arabic)
2. Check PDF encoding and font embedding
3. Try alternative PDF if extraction fails
4. Fallback to pdfplumber (auto-attempted)

### Problem: ChromaDB persistence errors
**Symptom:** `Collection not found` or `Permission denied`

**Solution:**
1. Check write permissions on `storage/chroma/`
2. Delete `storage/chroma/` and rebuild
3. Run scripts with same user account

---

## Testing | الاختبار

Run unit tests:

```bash
conda activate exp

# Test chunking
python tests/test_chunking.py

# Test employee database
python tests/test_db.py

# Full sanity check
python scripts/sanity_demo.py
```

---

## Development | التطوير

### Adding New Features

**Custom Routing Rules:**
Edit `hr_agent/routing.py` to add keywords

**New Database Fields:**
1. Update `EmployeeModel` in `hr_agent/db.py`
2. Update `generate_synthetic_employees()`
3. Rebuild database: `python scripts/build_employee_db.py`

**Different LLM Prompts:**
Edit `_generate_llm_answer()` in `hr_agent/rag.py`

**Custom Chunking:**
Adjust parameters in `config.py` or `hr_agent/chunking.py`

### Code Quality

- Modular architecture (separate concerns)
- Type hints where applicable
- Logging throughout
- Graceful fallbacks (missing models, GPU, etc.)
- Arabic-optimized (RTL, proper word counting, etc.)

---

## Performance Notes | ملاحظات الأداء

**Typical Performance (on GPU):**
- PDF ingestion: ~2-5 minutes (150-page PDF)
- Embedding generation: ~1-3 minutes (500 chunks)
- Query retrieval: <1 second
- LLM generation: 2-5 seconds (depends on model size)

**CPU-only mode:**
- 5-10x slower, but fully functional
- Consider smaller models

**Memory Usage:**
- BGE-M3: ~1-2 GB VRAM
- Qwen-1.7B: ~3-4 GB VRAM (float16)
- With 4-bit: ~1-2 GB VRAM
- ChromaDB: ~100-500 MB RAM (depends on chunk count)

---

## Security & Privacy | الأمان والخصوصية

- ✅ 100% local processing (no data sent to external APIs)
- ✅ Synthetic employee data (not real individuals)
- ✅ Policy PDF is authoritative source
- ⚠️ Never invent legal rules (grounded in document)
- ⚠️ For production: add authentication, audit logs, etc.

---

## License | الترخيص

This is a demo/prototype for educational purposes.

Saudi labor bylaws: Use official government sources for legal compliance.

---

## Support | الدعم

**Issues:**
- Check troubleshooting section above
- Review logs in console output
- Verify all paths and models exist

**Configuration Help:**
```bash
python config.py  # Print current config and warnings
```

**Logs:**
- Detailed logs printed to console
- Check for ERROR/WARNING messages

---

## Changelog | سجل التغييرات

**v1.0.0** (2026-01-26)
- Initial release
- RAG over Arabic PDF
- 1000 synthetic employees
- Streamlit UI with Arabic support
- Query routing (DB/RAG/Hybrid)
- Local model support (BGE-M3 + Qwen)
- Full offline operation

---

## Acknowledgments | شكر وتقدير

**Technologies:**
- Hugging Face Transformers
- ChromaDB
- Streamlit
- PyMuPDF
- SQLAlchemy

**Models:**
- BAAI/bge-m3 (Beijing Academy of AI)
- Qwen (Alibaba Cloud)

---

## Quick Start Checklist | قائمة التحقق السريعة

- [ ] Conda env `exp` activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] PDF placed at `/home/hr_case/اللائحة التنفيذية لنظام العمل وملحقاتها.pdf`
- [ ] Embedding model downloaded to `models1/BAAI__bge-m3/`
- [ ] LLM model downloaded to `models1/Qwen__Qwen3-1.7B/`
- [ ] Employee DB built (`python scripts/build_employee_db.py`)
- [ ] PDF ingested (`python scripts/ingest_pdf.py`)
- [ ] Sanity check passed (`python scripts/sanity_demo.py`)
- [ ] Streamlit app running (`streamlit run app/app.py`)

---

**مبني بـ ❤️ للابتكار في الموارد البشرية في السعودية**
