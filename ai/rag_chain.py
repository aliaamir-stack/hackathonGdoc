"""
PULSE MedFact RAG Chain
M3 -- AI/ML Engineer

Pipeline:
  claim -> embed -> ChromaDB similarity search -> Gemini synthesis -> verdict + citations

Connects to ChromaDB running on localhost:8001
The 'medical_facts' collection is populated by M4's PubMed ingestion script.
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer
from typing import Optional
from dotenv import load_dotenv

from .gemini_client import gemini
from .prompts import MEDFACT_SYSTEM_PROMPT

load_dotenv()

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8001))
CHROMA_PATH = os.getenv("CHROMA_PATH", "./backend/chroma_db")
COLLECTION_NAME = "medical_facts"
TOP_K_CHUNKS = 5


class MedFactVerifier:
    """
    RAG pipeline for MedFact Shield.

    Usage:
        verifier = MedFactVerifier()
        result = verifier.verify("Lemon juice cures dengue fever")
        # result = {
        #   "verdict": "FALSE",
        #   "confidence": 0.92,
        #   "summary": "...",
        #   "citations": [...],
        #   "sub_claims": [...],
        #   "safe_advice": "..."
        # }
    """

    def __init__(self):
        print("[MedFactVerifier] Loading SentenceTransformer model...")
        self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
        print("[MedFactVerifier] Connecting to ChromaDB...")
        # Use PersistentClient for direct local access (faster, no HTTP needed)
        # Falls back to HttpClient if CHROMA_PATH not found
        import os as _os
        if _os.path.exists(CHROMA_PATH):
            self._chroma = chromadb.PersistentClient(path=CHROMA_PATH)
            print("[MedFactVerifier] Using PersistentClient at " + CHROMA_PATH)
        else:
            self._chroma = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            print("[MedFactVerifier] Using HttpClient at " + CHROMA_HOST + ":" + str(CHROMA_PORT))
        self._collection = self._get_or_create_collection()
        print("[MedFactVerifier] Ready. Collection '" + COLLECTION_NAME + "' has " + str(self._collection.count()) + " chunks.")

    def _get_or_create_collection(self):
        """Gets or creates the medical_facts collection in ChromaDB."""
        try:
            return self._chroma.get_collection(COLLECTION_NAME)
        except Exception:
            print("[MedFactVerifier] Collection not found -- creating empty collection.")
            print("[MedFactVerifier] NOTE: Run M4's pubmed_ingest.py first to populate it.")
            return self._chroma.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )

    def _embed(self, text: str) -> list:
        """Embeds a string using SentenceTransformers."""
        return self._embedder.encode(text).tolist()

    def _retrieve(self, claim: str, top_k: int = TOP_K_CHUNKS) -> list:
        """
        Performs cosine similarity search in ChromaDB.
        Returns a list of chunk dicts with 'text' and 'metadata'.
        """
        if self._collection.count() == 0:
            return []

        query_embedding = self._embed(claim)
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self._collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append({
                "text": doc,
                "metadata": meta,
                "similarity": round(1 - dist, 4),
            })

        return chunks

    def _build_context_block(self, chunks: list) -> str:
        """Formats retrieved chunks into the Gemini prompt context."""
        if not chunks:
            return "No relevant medical literature found in the knowledge base."

        lines = []
        for i, chunk in enumerate(chunks, 1):
            meta = chunk.get("metadata", {})
            title = meta.get("title", "Unknown Paper")
            pmid = meta.get("pmid", "N/A")
            sim = chunk.get("similarity", 0)
            lines.append(
                "[CHUNK " + str(i) + "] (similarity=" + str(sim) + ", PMID=" + str(pmid) + ")\n"
                "Title: " + str(title) + "\n"
                "Text: " + str(chunk["text"]) + "\n"
            )
        return "\n".join(lines)

    def verify(self, claim: str) -> dict:
        """
        Main entry point. Verifies a health claim against medical literature.

        Args:
            claim: The health claim to verify (e.g., "Haldi doodh cures COVID-19")

        Returns:
            dict with verdict, confidence, summary, citations, sub_claims, safe_advice
        """
        print("[MedFactVerifier] Verifying claim: '" + claim[:80] + "...'")

        # Step 1: Retrieve relevant chunks
        chunks = self._retrieve(claim)
        context_block = self._build_context_block(chunks)

        # Step 2: Build the prompt
        prompt = (
            "HEALTH CLAIM TO VERIFY:\n"
            "\"" + claim + "\"\n\n"
            "MEDICAL LITERATURE CONTEXT:\n"
            + context_block +
            "\n\nBased ONLY on the above context chunks, evaluate the claim and return your JSON response.\n"
        )

        # Step 3: Call Gemini with the RAG system prompt
        try:
            result = gemini.generate_json(
                prompt=prompt,
                system_prompt=MEDFACT_SYSTEM_PROMPT,
                temperature=0.1,
            )
        except Exception as e:
            print("[MedFactVerifier] Gemini call failed: " + str(e))
            result = {
                "verdict": "UNVERIFIED",
                "confidence": 0.0,
                "summary": "Unable to verify this claim due to a service error. Please consult a doctor.",
                "citations": [],
                "sub_claims": [],
                "safe_advice": "Please consult a qualified healthcare professional.",
            }

        # Step 4: Attach raw chunk metadata for transparency
        result["_chunks_retrieved"] = len(chunks)
        result["_top_similarity"] = chunks[0]["similarity"] if chunks else 0.0

        print("[MedFactVerifier] Verdict: " + str(result.get("verdict")) + " (confidence=" + str(result.get("confidence")) + ")")
        return result

    def add_document(self, text: str, metadata: dict, doc_id: str) -> None:
        """
        Adds a single document chunk to ChromaDB.
        Called by M4's ingestion script.
        """
        embedding = self._embed(text)
        self._collection.upsert(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[doc_id],
        )

    def collection_count(self) -> int:
        return self._collection.count()
