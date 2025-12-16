import sys
from pathlib import Path
import os

# Ensure project root is importable (so "src" package is found)
ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

# Default env vars for tests
os.environ.setdefault("SERPER_API_KEY", "test-serper-key")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("MODEL", "gpt-4o-mini")
