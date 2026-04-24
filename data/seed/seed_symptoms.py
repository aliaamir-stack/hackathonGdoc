import os
import sys
import random
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from data.utils.db import get_supabase_client

load_dotenv()
supabase = get_supabase_client()

CITIES = [
    {"name": "Karachi", "lat_range": (24.74, 24.97), "lng_range": (66.94, 67.19), "weight": 0.5},
    {"name": "Lahore", "lat_range": (31.41, 31.65), "lng_range": (74.17, 74.42), "weight": 0.3},
    {"name": "Islamabad", "lat_range": (33.60, 33.77), "lng_range": (72.97, 73.17), "weight": 0.2},
]
SYMPTOMS = ["fever", "dengue-like", "GI", "respiratory"]

def seed_reports(total: int = 300):
    print(f"Generating {total} mock symptom reports...")
    reports = []
    now = datetime.now(timezone.utc)
    
    for _ in range(total):
        r = random.random()
        if r < 0.5: city = CITIES[0]
        elif r < 0.8: city = CITIES[1]
        else: city = CITIES[2]
            
        reports.append({
            "latitude": random.uniform(*city["lat_range"]),
            "longitude": random.uniform(*city["lng_range"]),
            "symptoms": [random.choice(SYMPTOMS)],
            "urgency_level": random.randint(1, 5),
            "created_at": (now - timedelta(days=random.uniform(0, 3))).isoformat()
        })
        
    print("Clearing existing seed reports to prevent duplicates...")
    supabase.table("symptom_reports").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    print("Inserting into Supabase...")
    batch_size = 100
    total_inserted = 0
    for i in range(0, len(reports), batch_size):
        batch = reports[i:i+batch_size]
        try:
            res = supabase.table("symptom_reports").insert(batch).execute()
            total_inserted += len(res.data)
            print(f"Inserted {total_inserted}/{len(reports)} reports...")
        except Exception as e:
            print(f"Error inserting batch: {e}")
            
    print("Seeding complete.")

if __name__ == "__main__":
    seed_reports()
