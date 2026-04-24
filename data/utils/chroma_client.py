import os
import chromadb

def get_chroma_client():
    # Path to backend/chroma_db/ as per file structure
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "chroma_db"))
    os.makedirs(db_path, exist_ok=True)
    return chromadb.PersistentClient(path=db_path)

def get_db_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "chroma_db"))
