import sys
import os

# Add sharesense folder to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sharesense'))

from app import create_app
from database import init_db

init_db()
app = create_app()
