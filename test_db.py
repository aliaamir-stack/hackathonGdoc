import os
import chromadb
from dotenv import load_dotenv

load_dotenv()

print("Testing ChromaDB...")
try:
    chroma_client = chromadb.HttpClient(host=os.getenv("CHROMA_HOST", "localhost"), port=os.getenv("CHROMA_PORT", 8001))
    collections = chroma_client.list_collections()
    print(f"Success! ChromaDB is running. Found collections: {[c.name for c in collections]}")
except Exception as e:
    print(f"Failed to connect to ChromaDB: {e}")

print("\nTesting Supabase Postgres via psycopg2...")
try:
    import psycopg2
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    tables = cur.fetchall()
    print(f"Success! Supabase DB is running. Found tables: {[t[0] for t in tables]}")
    conn.close()
except Exception as e:
    print(f"Failed to connect to Supabase: {e}")

print("\nTesting Gemini...")
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Say hello concisely.")
    print(f"Success! Gemini says: {response.text.strip()}")
except Exception as e:
    print(f"Failed to connect to Gemini: {e}")
