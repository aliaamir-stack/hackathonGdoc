import os
import sys
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from data.utils.db import get_supabase_client
from data.utils.chroma_client import get_chroma_client
from data.utils.embeddings import get_embedding_function

load_dotenv()
supabase = get_supabase_client()

WHO_RSS_URL = "https://www.who.int/rss-feeds/news-english.xml"

def ingest_who_rss():
    print(f"Fetching WHO RSS from {WHO_RSS_URL}...")
    try:
        response = requests.get(WHO_RSS_URL)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        alerts = []
        texts = []
        metadatas = []
        ids = []
        
        for item in root.findall('.//item'):
            title = item.findtext('title', '')
            description = item.findtext('description', '')
            link = item.findtext('link', '')
            
            alerts.append({"title": title, "description": description, "link": link})
            texts.append(f"Title: {title}\nDescription: {description}")
            metadatas.append({"source": "WHO", "link": link})
            ids.append(link)
            
        if not alerts:
            print("No RSS items found.")
            return
            
        print(f"Parsed {len(alerts)} items. Inserting into Supabase...")
        try:
            res = supabase.table("outbreak_alerts").insert(alerts).execute()
            print(f"Inserted {len(res.data)} alerts into Supabase.")
        except Exception as e:
            print(f"Error inserting to Supabase: {e}")
            
        print("Embedding into ChromaDB...")
        client = get_chroma_client()
        emb_fn = get_embedding_function()
        collection = client.get_or_create_collection(name="who_alerts", embedding_function=emb_fn)
        collection.upsert(documents=texts, metadatas=metadatas, ids=ids)
        print("ChromaDB embedding complete.")
    except Exception as e:
        print(f"Error during WHO RSS ingestion: {e}")

if __name__ == "__main__":
    ingest_who_rss()
