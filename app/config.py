from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
REPO_DIR = DATA_DIR / "repo"
INDEX_DIR = DATA_DIR / "index"
DOCS_DIR = DATA_DIR / "docs"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Groq config
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# Pick a good general model – adjust if you like
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"
