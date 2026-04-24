import os
import argparse
from typing import List, Dict, Any
from Bio import Entrez
import time
from dotenv import load_dotenv

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from data.utils.chroma_client import get_chroma_client, get_db_path
from data.utils.embeddings import get_embedding_function

load_dotenv()

# Setup Entrez
Entrez.email = "pulse_hackathon@example.com"
api_key = os.getenv("NCBI_API_KEY")
if api_key and api_key != "your_ncbi_key":
    Entrez.api_key = api_key

TERMS = [
    "dengue[tiab]",
    "typhoid[tiab]",
    "malaria[tiab]",
    "COVID-19[tiab]",
    "hypertension[tiab]",
    "diabetes mellitus[tiab]",
    "cholera[tiab]",
    "tuberculosis Pakistan[tiab]"
]

def fetch_pubmed_abstracts(query: str, max_results: int = 700) -> List[Dict[str, Any]]:
    print(f"Searching PubMed for: {query}")
    try:
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        
        id_list = record["IdList"]
        if not id_list:
            return []
            
        print(f"Fetching {len(id_list)} abstracts...")
        handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
        articles = Entrez.read(handle)
        handle.close()
        
        results = []
        for article in articles.get('PubmedArticle', []):
            try:
                medline = article['MedlineCitation']
                pmid = str(medline['PMID'])
                article_info = medline['Article']
                title = article_info.get('ArticleTitle', '')
                
                abstract_text = ""
                if 'Abstract' in article_info and 'AbstractText' in article_info['Abstract']:
                    abstract_parts = article_info['Abstract']['AbstractText']
                    abstract_text = " ".join([str(p) for p in abstract_parts])
                
                if abstract_text:
                    results.append({
                        "id": pmid,
                        "title": title,
                        "abstract": abstract_text,
                        "query": query
                    })
            except Exception as e:
                continue
                
        return results
    except Exception as e:
        print(f"Error fetching {query}: {e}")
        return []

def load_and_embed(texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str], collection_name: str = "medical_facts"):
    print(f"Initializing ChromaDB at {get_db_path()}...")
    client = get_chroma_client()
    emb_fn = get_embedding_function()
    
    collection = client.get_or_create_collection(name=collection_name, embedding_function=emb_fn)
    
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        print(f"Adding batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size} to ChromaDB...")
        collection.upsert(
            documents=texts[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )
    print("Batch load complete.")

def main(test_mode: bool = False):
    all_texts = []
    all_metadatas = []
    all_ids = []
    
    queries = TERMS
    max_res = 700
    
    if test_mode:
        print("RUNNING IN TEST MODE - Only fetching a few records.")
        queries = ["dengue[tiab]"]
        max_res = 5
        
    for query in queries:
        abstracts = fetch_pubmed_abstracts(query, max_results=max_res)
        print(f"Fetched {len(abstracts)} valid abstracts for {query}")
        
        for item in abstracts:
            if item['id'] not in all_ids:
                all_ids.append(item['id'])
                all_texts.append(f"Title: {item['title']}\nAbstract: {item['abstract']}")
                all_metadatas.append({
                    "title": item['title'],
                    "source": "PubMed",
                    "query": item['query']
                })
        
        time.sleep(0.5)
        
    if all_texts:
        print(f"Total unique abstracts to embed: {len(all_texts)}")
        load_and_embed(all_texts, all_metadatas, all_ids)
        print("Ingestion complete. ChromaDB is populated.")
    else:
        print("No abstracts found to ingest.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest PubMed abstracts into ChromaDB")
    parser.add_argument("--test-mode", action="store_true", help="Run with limited queries for testing")
    args = parser.parse_args()
    
    main(test_mode=args.test_mode)
