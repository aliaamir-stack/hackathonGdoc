async def verify_health_claim(claim: str):
    return {
        "verdict": "FALSE",
        "confidence": 0.9,
        "sub_claims": [claim],
        "citations": [
            {
                "title": "Example PubMed citation",
                "source": "PubMed",
                "url": "https://pubmed.ncbi.nlm.nih.gov/",
            }
        ],
        "summary": "Fallback verifier: replace with M3 implementation.",
    }
