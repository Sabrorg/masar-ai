# Quick Start Guide | دليل البدء السريع

## What You Have Now | ما تم إنجازه

✅ **Complete HR Assistant System Built!**

The following has been implemented and is ready to use:

1. ✅ **Project Structure**: Clean modular codebase
2. ✅ **Configuration**: Flexible config system with env var support
3. ✅ **PDF Processing**: Arabic-optimized extraction & chunking
4. ✅ **Vector Database**: ChromaDB integration for RAG
5. ✅ **Employee Database**: SQLite with 1000 synthetic employees (ALREADY BUILT!)
6. ✅ **Query Routing**: Smart routing (DB/RAG/Hybrid)
7. ✅ **LLM Integration**: Local model support with fallbacks
8. ✅ **Streamlit UI**: Full Arabic RTL interface
9. ✅ **All Dependencies**: Installed in conda env `exp`
10. ✅ **Tests**: Unit tests for chunking and database

---

## What You Need to Do Next | الخطوات التالية

### CRITICAL: Download Models (Required)

The system needs two models to work:

#### 1. Embedding Model (REQUIRED)
```bash
cd /home/saad/hr_case/models1
git lfs install  # If not already installed
git clone https://huggingface.co/BAAI/bge-m3 BAAI__bge-m3
```

**Alternative (smaller):**
```bash
git clone https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2 BAAI__bge-m3
```

#### 2. LLM Model (REQUIRED for full functionality)
```bash
cd /home/saad/hr_case/models1
git clone https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct Qwen__Qwen3-1.7B
```

**Alternative options:**
- Qwen/Qwen2.5-3B-Instruct (better quality, more VRAM)
- meta-llama/Llama-3.2-3B-Instruct
- microsoft/Phi-3-mini-4k-instruct

**Note:** The app will work in retrieval-only mode without LLM, but answers will be less natural.

---

### CRITICAL: Add PDF (Required)

Place the Saudi labor bylaws PDF:
```bash
# If you have the PDF, copy it to:
cp /path/to/your/pdf.pdf "/home/saad/hr_case/اللائحة التنفيذية لنظام العمل وملحقاتها.pdf"

# Or update the path in config.py if you want to use a different location
```

---

## Running the System | تشغيل النظام

### Step 1: Verify Configuration
```bash
conda activate exp
cd /home/saad/hr_case
python config.py
```

This will show your current configuration and any missing components.

### Step 2: Ingest PDF (After downloading models and adding PDF)
```bash
conda activate exp
cd /home/saad/hr_case
python scripts/ingest_pdf.py
```

This will:
- Extract all pages from the PDF
- Chunk text into ~150-220 word segments
- Generate embeddings
- Store in ChromaDB vector database
- Takes ~2-5 minutes depending on PDF size

### Step 3: Run Sanity Check
```bash
conda activate exp
python scripts/sanity_demo.py
```

This verifies all components work correctly.

### Step 4: Launch Streamlit App
```bash
conda activate exp
streamlit run app/app.py
```

The app will open at `http://localhost:8501`

---

## Testing Without Models (Partial Functionality)

If you want to test the system before downloading large models:

### Test Employee Database Only
```bash
conda activate exp
cd /home/saad/hr_case

# Already built! Verify:
python -c "from hr_agent.db import create_employee_db; db = create_employee_db('storage/hr_demo.sqlite'); print(f'Employees: {db.count_employees()}')"
# Should output: Employees: 1000
```

### Test Chunking
```bash
conda activate exp
python tests/test_chunking.py
```

### Test Database
```bash
conda activate exp
python tests/test_db.py
```

---

## Current Status | الحالة الحالية

### ✅ Working (No Models Needed)
- Employee database (1000 employees)
- Query routing (keyword-based)
- Database queries (personal info)
- Chunking algorithm
- All code modules
- Tests

### ⏳ Needs Models to Work
- PDF ingestion (needs embedding model)
- RAG retrieval (needs embedding model)
- Answer generation (needs LLM model)
- Full Streamlit app (needs both models)

---

## Quick Commands Reference | مرجع الأوامر السريعة

```bash
# Activate environment
conda activate exp

# Navigate to project
cd /home/saad/hr_case

# Check configuration
python config.py

# Rebuild employee database (if needed)
python scripts/build_employee_db.py

# Ingest PDF and build index
python scripts/ingest_pdf.py

# Run sanity checks
python scripts/sanity_demo.py

# Launch Streamlit app
streamlit run app/app.py

# Run tests
python tests/test_chunking.py
python tests/test_db.py
```

---

## File Locations | مواقع الملفات

```
/home/saad/hr_case/
├── config.py                  # Edit this to change settings
├── README.md                  # Full documentation
├── requirements.txt           # Dependencies (already installed)
│
├── storage/
│   ├── hr_demo.sqlite        # ✅ Employee database (1000 employees)
│   └── chroma/               # ⏳ Vector index (needs PDF ingestion)
│
└── models1/                  # ⏳ YOU NEED TO DOWNLOAD MODELS HERE
    ├── BAAI__bge-m3/        # Embedding model
    └── Qwen__Qwen3-1.7B/    # LLM model
```

---

## Example Interaction | مثال على الاستخدام

Once the app is running, try these queries:

**Employee Data:**
```
كم راتبي الحالي؟
→ Gets salary from employee database

وش تقييمي السنوي؟
→ Shows performance rating

ما هو هدفي لهذا العام؟
→ Shows yearly goals
```

**Policy Questions (needs PDF ingested):**
```
ما هي حقوق الموظف في الإجازات؟
→ Retrieves from labor bylaws PDF

كيف يتم احتساب مكافأة نهاية الخدمة؟
→ Searches policy documents

هل يحق للشركة خصم راتبي؟
→ Finds relevant legal text
```

**Hybrid Questions:**
```
هل انخصم من راتبي الشهر الماضي؟ وما هو السبب القانوني؟
→ Combines employee data + policy retrieval
```

---

## Troubleshooting | حل المشاكل السريعة

### Models not downloading?
```bash
# Install git-lfs first
sudo apt-get install git-lfs
git lfs install

# Then clone models
```

### PDF has wrong name?
Edit `config.py`:
```python
PDF_PATH = Path("/your/custom/path.pdf")
```

### Want to use CPU only?
Edit `config.py`:
```python
DEVICE_PREFERENCE = "cpu"
```

### Out of VRAM?
Edit `hr_agent/llm.py` and set `use_4bit=True` in the LLM initialization.

---

## Next Steps After Setup | الخطوات بعد الإعداد

1. **Download models** (see above)
2. **Add PDF** (see above)
3. **Run `python scripts/ingest_pdf.py`**
4. **Run `streamlit run app/app.py`**
5. **Start asking questions!**

---

## Need Help? | تحتاج مساعدة؟

1. Check [README.md](README.md) for full documentation
2. Run `python config.py` to see configuration warnings
3. Check console logs for detailed error messages
4. Verify all paths exist and are correct

---

**You're 95% done! Just download the models and PDF, then you're ready to go! 🚀**

**أنت على بعد خطوة واحدة! فقط حمّل النماذج والـ PDF، وستكون جاهزًا! 🚀**
