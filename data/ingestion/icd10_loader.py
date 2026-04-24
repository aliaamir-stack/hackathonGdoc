import os
import sys
import pandas as pd
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from data.utils.db import get_supabase_client

load_dotenv()
supabase = get_supabase_client()

# Adjust path based on project root
ICD10_CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datafiles", "icd10.csv"))

def load_icd10():
    if not os.path.exists(ICD10_CSV_PATH):
        print(f"Error: Could not find ICD-10 CSV at {ICD10_CSV_PATH}")
        print("Please ensure the file is placed there or update the path.")
        return

    print(f"Reading {ICD10_CSV_PATH}...")
    try:
        df = pd.read_csv(ICD10_CSV_PATH, header=None, names=["code", "description"])
        df["category"] = None
        df["chapter"] = None
        
        records = df.to_dict(orient="records")
        print(f"Loaded {len(records)} records from CSV.")
        
        batch_size = 1000
        total_inserted = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            try:
                response = supabase.table("icd10_codes").upsert(batch).execute()
                total_inserted += len(response.data)
                print(f"Inserted {total_inserted}/{len(records)}...")
            except Exception as e:
                print(f"Error inserting batch: {e}")
                
        print("ICD-10 loading complete.")
    except Exception as e:
        print(f"Error processing ICD-10 file: {e}")

if __name__ == "__main__":
    load_icd10()
