"""
Configuration module for HR Assistant Demo
Supports environment variable overrides
"""
import os
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", "/home/saad/hr_case"))
PDF_PATH = Path(os.getenv("PDF_PATH", PROJECT_ROOT / "اللائحة التنفيذية لنظام العمل وملحقاتها.pdf"))

# Storage paths
STORAGE_DIR = PROJECT_ROOT / "storage"
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", STORAGE_DIR / "chroma"))
SQLITE_PATH = Path(os.getenv("SQLITE_PATH", STORAGE_DIR / "hr_demo.sqlite"))

# Model paths (local only)
MODELS_DIR = PROJECT_ROOT / "models1"
EMBED_MODEL_PATH = Path(os.getenv("EMBED_MODEL_PATH", MODELS_DIR / "BAAI__bge-m3"))
LLM_MODEL_PATH = Path(os.getenv("LLM_MODEL_PATH", MODELS_DIR / "Qwen__Qwen3-1.7B"))

# Device configuration
DEVICE_PREFERENCE = os.getenv("DEVICE_PREFERENCE", "cuda")  # cuda or cpu

# Synthetic data configuration
EMPLOYEE_COUNT = int(os.getenv("EMPLOYEE_COUNT", "1000"))

# Retrieval configuration
TOP_K = int(os.getenv("TOP_K", "6"))

# Chunking configuration
CHUNK_MIN_WORDS = int(os.getenv("CHUNK_MIN_WORDS", "150"))
CHUNK_MAX_WORDS = int(os.getenv("CHUNK_MAX_WORDS", "220"))
CHUNK_OVERLAP_WORDS = int(os.getenv("CHUNK_OVERLAP_WORDS", "50"))

# ChromaDB configuration
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "saudi_labor_policy")

# LLM configuration
LLM_MAX_NEW_TOKENS = int(os.getenv("LLM_MAX_NEW_TOKENS", "512"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

# Random seed for reproducibility
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))

# Ensure storage directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

def validate_config():
    """Validate configuration and provide helpful error messages"""
    issues = []

    if not PDF_PATH.exists():
        issues.append(f"⚠️  PDF not found at: {PDF_PATH}")
        issues.append(f"   Please place the Arabic PDF at this location.")

    if not EMBED_MODEL_PATH.exists():
        issues.append(f"⚠️  Embedding model not found at: {EMBED_MODEL_PATH}")
        issues.append(f"   Please download the model and place it at this location.")
        issues.append(f"   Or set EMBED_MODEL_PATH environment variable.")

    if not LLM_MODEL_PATH.exists():
        issues.append(f"⚠️  LLM model not found at: {LLM_MODEL_PATH}")
        issues.append(f"   Please download the model and place it at this location.")
        issues.append(f"   Or set LLM_MODEL_PATH environment variable.")
        issues.append(f"   App will run in retrieval-only mode without LLM.")

    return issues

def print_config():
    """Print current configuration"""
    print("=" * 60)
    print("HR ASSISTANT CONFIGURATION")
    print("=" * 60)
    print(f"Project Root:      {PROJECT_ROOT}")
    print(f"PDF Path:          {PDF_PATH}")
    print(f"ChromaDB Dir:      {CHROMA_DIR}")
    print(f"SQLite Path:       {SQLITE_PATH}")
    print(f"Embedding Model:   {EMBED_MODEL_PATH}")
    print(f"LLM Model:         {LLM_MODEL_PATH}")
    print(f"Device:            {DEVICE_PREFERENCE}")
    print(f"Employee Count:    {EMPLOYEE_COUNT}")
    print(f"Top-K Retrieval:   {TOP_K}")
    print(f"Chunk Size:        {CHUNK_MIN_WORDS}-{CHUNK_MAX_WORDS} words")
    print(f"Chunk Overlap:     {CHUNK_OVERLAP_WORDS} words")
    print("=" * 60)

    issues = validate_config()
    if issues:
        print("\n⚠️  CONFIGURATION WARNINGS:")
        for issue in issues:
            print(issue)
        print()

if __name__ == "__main__":
    print_config()
