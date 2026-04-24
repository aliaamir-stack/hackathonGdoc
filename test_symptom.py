"""
M3 Phase 3 -- Symptom Navigator PDF Test
Simulates a conversation about Dengue fever symptoms and generates a triage PDF report.
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from ai.symptom_engine import SymptomNavigator, generate_triage_pdf

print("=" * 70)
print("PULSE Symptom Navigator Test")
print("=" * 70)

navigator = SymptomNavigator(session_id="test_session_123")

# Simulated multi-turn conversation matching our mock API strings
print("User: I have a fever and severe joint pain.")
response_1 = navigator.chat("I have a fever and severe joint pain.")
print(f"AI  : {response_1['reply']}\n")

print("User: My fever is 103F and I noticed a rash on my arm.")
response_2 = navigator.chat("My fever is 103F and I noticed a rash on my arm.")
print(f"AI  : {response_2['reply']}\n")

if response_2.get("triage"):
    print("=" * 70)
    print("Triage Summary Generated:")
    print(response_2["triage"])
    print("=" * 70)

    pdf_bytes = generate_triage_pdf(response_2)
    pdf_path = os.path.join(os.getcwd(), "triage_report.pdf")
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    
    print(f"\nSUCCESS: PDF Report generated at -> {pdf_path}")
else:
    print("\nERROR: Triage summary was not generated. Mock API may have failed.")
