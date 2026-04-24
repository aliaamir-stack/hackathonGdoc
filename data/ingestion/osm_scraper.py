import os
import sys
import requests
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from data.utils.db import get_supabase_client

load_dotenv()
supabase = get_supabase_client()

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_QUERY = """
[out:json][timeout:90];
(
  node["amenity"="hospital"](23.69,60.87,37.08,77.84);
  node["amenity"="pharmacy"](23.69,60.87,37.08,77.84);
  node["amenity"="blood_bank"](23.69,60.87,37.08,77.84);
);
out body;
"""

def scrape_osm():
    print("Querying OSM Overpass API...")
    try:
        headers = {
            "User-Agent": "PULSE_Hackathon_Data_Ingestion/1.0",
            "Accept": "application/json"
        }
        response = requests.post(OVERPASS_URL, data={'data': OVERPASS_QUERY}, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        elements = data.get("elements", [])
        print(f"Found {len(elements)} facilities.")
        
        facilities = []
        for el in elements:
            if "tags" not in el:
                continue
            tags = el["tags"]
            
            fac_type = "unknown"
            if tags.get("amenity") == "hospital":
                fac_type = "hospital"
            elif tags.get("amenity") == "pharmacy":
                fac_type = "pharmacy"
            elif tags.get("amenity") == "blood_bank":
                fac_type = "blood_bank"
                
            if fac_type == "unknown":
                continue
                
            name = tags.get("name", f"Unnamed {fac_type.capitalize()}")
            address_parts = [tags[tag] for tag in ["addr:street", "addr:city", "addr:postcode"] if tags.get(tag)]
            address = ", ".join(address_parts) if address_parts else None
            
            facilities.append({
                "name": name,
                "type": fac_type,
                "latitude": el.get("lat"),
                "longitude": el.get("lon"),
                "address": address
            })
            
        if not facilities:
            print("No valid facilities to insert.")
            return
            
        print("Clearing existing facilities to prevent duplicates (and fixing the current duplicates)...")
        supabase.table("facilities").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        new_facilities = facilities

        print(f"Inserting {len(new_facilities)} new facilities into Supabase...")
        batch_size = 500
        total_inserted = 0
        for i in range(0, len(new_facilities), batch_size):
            batch = new_facilities[i:i+batch_size]
            try:
                res = supabase.table("facilities").insert(batch).execute()
                total_inserted += len(res.data)
                print(f"Inserted {total_inserted}/{len(new_facilities)} facilities...")
            except Exception as e:
                print(f"Error inserting batch: {e}")
                
        print("OSM scraping and insertion complete.")
    except Exception as e:
        print(f"Error during OSM scraping: {e}")

if __name__ == "__main__":
    scrape_osm()
