import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from data.utils.db import get_supabase_client
from data.utils.chroma_client import get_chroma_client

load_dotenv()
supabase = get_supabase_client()
chroma_client = get_chroma_client()

def get_supabase_count(table: str) -> int:
    try:
        res = supabase.table(table).select("*", count="exact", head=True).execute()
        return res.count if res.count is not None else 0
    except Exception as e:
        print(f"Error counting {table}: {e}")
        return 0

def get_chroma_count(collection_name: str) -> int:
    try:
        collection = chroma_client.get_collection(name=collection_name)
        return collection.count()
    except Exception as e:
        print(f"Error counting chroma collection {collection_name}: {e}")
        return 0

def print_summary():
    print("="*40)
    print(" PULSE DATA PIPELINE SUMMARY")
    print("="*40)
    print("Supabase Tables:")
    print(f" - symptom_reports : {get_supabase_count('symptom_reports')}")
    print(f" - facilities      : {get_supabase_count('facilities')}")
    print(f" - icd10_codes     : {get_supabase_count('icd10_codes')}")
    print(f" - drug_interactions: {get_supabase_count('drug_interactions')}")
    print(f" - outbreak_alerts : {get_supabase_count('outbreak_alerts')}")
    print(f" - users           : {get_supabase_count('users')}")
    
    print("\nChromaDB Collections (Local: backend/chroma_db):")
    print(f" - medical_facts   : {get_chroma_count('medical_facts')}")
    print(f" - who_alerts      : {get_chroma_count('who_alerts')}")
    print("="*40)

if __name__ == "__main__":
    print_summary()
