import sys
import os

# Add sharesense folder to path so imports work
_sharesense_dir = os.path.join(os.path.dirname(__file__), '..', 'sharesense')
sys.path.insert(0, _sharesense_dir)

from app import create_app
from database import init_db

try:
    init_db()
except Exception as e:
    print(f"DB init warning: {e}")

app = create_app()
