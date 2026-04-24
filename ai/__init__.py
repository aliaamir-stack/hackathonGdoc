# Lazy imports — import directly from submodules to avoid circular issues
# e.g.: from ai.gemini_client import gemini
#       from ai.rag_chain import MedFactVerifier
#       from ai.symptom_engine import SymptomNavigator, generate_triage_pdf

__all__ = ["gemini_client", "rag_chain", "symptom_engine", "prompts"]
