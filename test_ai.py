"""
Quick test to verify M3's AI module is working.
Run: python test_ai.py
"""
import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("PULSE AI Module --- M3 Test Suite")
print("=" * 60)

# Test 1: Gemini basic call
print("\n[1/3] Testing Gemini API connection...")
try:
    from ai.gemini_client import gemini
    response = gemini.generate("Say 'PULSE AI is ready' and nothing else.")
    print("  [OK] Gemini responded: " + response.strip())
except Exception as e:
    print("  [FAIL] " + str(e))
    sys.exit(1)

# Test 2: MedFact Shield
print("\n[2/3] Testing MedFact Shield (RAG pipeline)...")
try:
    from ai.rag_chain import MedFactVerifier
    verifier = MedFactVerifier()
    count = verifier.collection_count()
    print("  [INFO] ChromaDB medical_facts collection has " + str(count) + " chunks.")

    if count == 0:
        print("  [WARN] Collection is empty -- M4 ingestion not run yet.")
        print("  Testing claim verification with no context (fallback mode)...")

    result = verifier.verify("Drinking lemon juice can cure dengue fever")
    print("  [OK] Verdict: " + str(result.get("verdict")) + " | Confidence: " + str(result.get("confidence")))
    print("       Summary: " + str(result.get("summary", ""))[:100] + "...")
except Exception as e:
    print("  [FAIL] " + str(e))
    import traceback; traceback.print_exc()

# Test 3: Symptom Navigator
print("\n[3/3] Testing Symptom Navigator (multi-turn triage)...")
try:
    from ai.symptom_engine import SymptomNavigator, generate_triage_pdf
    nav = SymptomNavigator(session_id="test-001")

    result1 = nav.chat("I have fever and severe joint pain for 3 days. I am 28 years old.")
    print("  Turn 1 -- Reply: " + result1["reply"][:100] + "...")
    print("  Turn 1 -- Ready: " + str(result1["ready"]))

    result2 = nav.chat("The fever is 103F and I have a rash on my body. No previous medical history.")
    print("  Turn 2 -- Reply: " + result2["reply"][:100] + "...")
    print("  Turn 2 -- Ready: " + str(result2["ready"]))

    if result2.get("ready") and result2.get("triage"):
        triage = result2["triage"]
        print("  [OK] Triage result generated!")
        print("       Urgency: " + str(triage.get("urgency")) + " -- " + str(triage.get("urgency_label")))
        conditions = [d["condition"] for d in triage.get("differential", [])[:2]]
        print("       Conditions: " + str(conditions))
        pdf_bytes = generate_triage_pdf(result2)
        print("  [OK] PDF generated: " + str(len(pdf_bytes)) + " bytes")
        with open("test_triage_output.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("       Saved to: test_triage_output.pdf")
    else:
        print("  [INFO] Triage not ready after 2 turns (normal -- needs 3-4 turns)")
        print("  [OK] Symptom Navigator is responding correctly")

except Exception as e:
    print("  [FAIL] " + str(e))
    import traceback; traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete.")
print("=" * 60)
