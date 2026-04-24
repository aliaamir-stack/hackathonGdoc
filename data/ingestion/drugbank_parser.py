import os
import sys
import pandas as pd
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from data.utils.db import get_supabase_client

load_dotenv()
supabase = get_supabase_client()

# Adjust path based on project root
DRUG_INTERACTIONS_CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datafiles", "db_drug_interactions.csv"))

def load_drug_interactions():
    if not os.path.exists(DRUG_INTERACTIONS_CSV_PATH):
        print(f"Error: Could not find Drug Interactions CSV at {DRUG_INTERACTIONS_CSV_PATH}")
        print("Please ensure the file is placed there or update the path.")
        return

    print(f"Reading {DRUG_INTERACTIONS_CSV_PATH}...")
    try:
        df = pd.read_csv(DRUG_INTERACTIONS_CSV_PATH)
        
        df.rename(columns={"Drug 1": "drug_a", "Drug 2": "drug_b", "Interaction Description": "description"}, inplace=True)
        
        if 'drug_a' not in df.columns or 'drug_b' not in df.columns:
            print(f"Error: CSV does not have 'drug_a' and 'drug_b' columns. Found: {df.columns.tolist()}")
            return
            
        if 'description' not in df.columns:
            df['description'] = "Interaction found."
            
        records = df[['drug_a', 'drug_b', 'description']].to_dict(orient="records")
        print(f"Loaded {len(records)} interaction pairs from CSV.")
        
        print("Clearing existing drug interactions to prevent duplicates...")
        supabase.table("drug_interactions").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        batch_size = 1000
        total_inserted = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            try:
                response = supabase.table("drug_interactions").insert(batch).execute()
                total_inserted += len(response.data)
                print(f"Inserted {total_inserted}/{len(records)}...")
            except Exception as e:
                print(f"Error inserting batch: {e}")
                
        print("Drug interactions loading complete.")
    except Exception as e:
        print(f"Error processing drug interactions file: {e}")

if __name__ == "__main__":
    load_drug_interactions()
