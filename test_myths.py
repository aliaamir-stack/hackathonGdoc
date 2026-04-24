"""
M3 Phase 2 -- Pakistani WhatsApp Health Myths Test Suite
Tests 10 real health claims circulating on WhatsApp in Pakistan.
Results saved to myth_test_results.txt for review.
"""
import os, sys, time, json

os.chdir(os.path.dirname(os.path.abspath(__file__)))

OUTPUT_FILE = "myth_test_results.txt"

MYTHS = [
    {
        "id": 1,
        "claim": "Drinking lemon juice cures dengue fever and increases platelet count",
        "expected_verdict": "FALSE",
        "context": "Very common WhatsApp myth in Pakistan during dengue season"
    },
    {
        "id": 2,
        "claim": "Haldi doodh (turmeric milk) cures COVID-19 and prevents coronavirus infection",
        "expected_verdict": "MISLEADING",
        "context": "Spread widely during COVID-19 pandemic in Pakistan"
    },
    {
        "id": 3,
        "claim": "Taking Panadol (paracetamol) and Disprin (aspirin) together causes instant death",
        "expected_verdict": "FALSE",
        "context": "Dangerous myth that stops people from taking needed pain relief"
    },
    {
        "id": 4,
        "claim": "Drinking camel urine cures cancer and many serious diseases",
        "expected_verdict": "FALSE",
        "context": "Spread in religious contexts, dangerous as it can transmit MERS"
    },
    {
        "id": 5,
        "claim": "Eating raw garlic every morning prevents and cures tuberculosis (TB)",
        "expected_verdict": "MISLEADING",
        "context": "Common in rural Pakistan, people delay proper TB treatment"
    },
    {
        "id": 6,
        "claim": "Applying toothpaste on burns heals them faster and prevents scarring",
        "expected_verdict": "FALSE",
        "context": "Extremely common home remedy - actually causes serious infections"
    },
    {
        "id": 7,
        "claim": "Black seed (kalonji) oil cures every disease including diabetes and heart disease",
        "expected_verdict": "MISLEADING",
        "context": "Based on Hadith misquotation, sells as a miracle cure in Pakistan"
    },
    {
        "id": 8,
        "claim": "Children should not be vaccinated because vaccines cause autism",
        "expected_verdict": "FALSE",
        "context": "Major public health issue in Pakistan, causing polio outbreaks"
    },
    {
        "id": 9,
        "claim": "Drinking hot water with honey and ginger completely cures typhoid fever",
        "expected_verdict": "FALSE",
        "context": "People avoid antibiotics for typhoid and use this instead"
    },
    {
        "id": 10,
        "claim": "High fever in children should be treated with cold water baths and ice packs immediately",
        "expected_verdict": "MISLEADING",
        "context": "Dangerous advice -- can cause febrile seizures and shock"
    },
]

print("=" * 70)
print("PULSE MedFact Shield -- Pakistani Health Myths Test")
print("=" * 70)
print("Loading AI module (first load downloads SentenceTransformer)...")

from ai.rag_chain import MedFactVerifier
verifier = MedFactVerifier()
print("Collection size:", verifier.collection_count(), "PubMed chunks")
print()

results = []
passed = 0
total = len(MYTHS)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("PULSE MedFact Shield -- Pakistani Myths Test Results\n")
    f.write("=" * 70 + "\n\n")

    for myth in MYTHS:
        print(f"[{myth['id']}/{total}] Testing: {myth['claim'][:60]}...")
        start = time.time()

        try:
            result = verifier.verify(myth["claim"])
            elapsed = round(time.time() - start, 1)

            verdict = result.get("verdict", "ERROR")
            confidence = result.get("confidence", 0)
            summary = result.get("summary", "")
            citations = result.get("citations", [])
            safe_advice = result.get("safe_advice", "")
            chunks = result.get("_chunks_retrieved", 0)

            verdict_match = verdict == myth["expected_verdict"]
            if verdict_match:
                passed += 1
                status = "[PASS]"
            else:
                status = "[DIFF]"  # different verdict -- not necessarily wrong

            print(f"  {status} Verdict: {verdict} (expected {myth['expected_verdict']}) | Confidence: {confidence} | {chunks} chunks | {elapsed}s")
            print(f"  Summary: {summary[:120]}...")

            # Write full result to file
            f.write(f"MYTH #{myth['id']}\n")
            f.write(f"Claim   : {myth['claim']}\n")
            f.write(f"Context : {myth['context']}\n")
            f.write(f"Verdict : {verdict} (expected: {myth['expected_verdict']}) {status}\n")
            f.write(f"Confidence: {confidence}\n")
            f.write(f"Chunks retrieved: {chunks} | Time: {elapsed}s\n")
            f.write(f"Summary : {summary}\n")
            f.write(f"Safe advice: {safe_advice}\n")
            if citations:
                f.write(f"Citations ({len(citations)}):\n")
                for c in citations:
                    f.write(f"  - {c.get('title', 'N/A')[:80]}\n")
                    f.write(f"    Finding: {c.get('finding', '')[:120]}\n")
            f.write("\n" + "-" * 70 + "\n\n")

            results.append({
                "id": myth["id"],
                "claim": myth["claim"],
                "verdict": verdict,
                "expected": myth["expected_verdict"],
                "confidence": confidence,
                "citations": len(citations),
                "chunks": chunks,
                "elapsed": elapsed,
                "status": status,
            })

        except Exception as e:
            print(f"  [ERROR] {e}")
            f.write(f"MYTH #{myth['id']} -- ERROR: {e}\n\n")
            results.append({"id": myth["id"], "verdict": "ERROR", "status": "[ERROR]"})

        # Rate limit safety: 15 req/min on Gemini free tier
        if myth["id"] < total:
            print("  (waiting 5s to respect rate limit...)")
            time.sleep(5)

    # Summary
    print()
    print("=" * 70)
    print(f"RESULTS: {passed}/{total} matched expected verdict")
    print(f"Full results saved to: {OUTPUT_FILE}")
    print("=" * 70)

    f.write("\nSUMMARY\n")
    f.write("=" * 70 + "\n")
    f.write(f"Total myths tested: {total}\n")
    f.write(f"Matched expected verdict: {passed}/{total}\n")
    f.write(f"Average confidence: {round(sum(r.get('confidence',0) for r in results)/total, 2)}\n")
    f.write(f"Average citations per claim: {round(sum(r.get('citations',0) for r in results)/total, 1)}\n")
    f.write(f"Average response time: {round(sum(r.get('elapsed',0) for r in results if 'elapsed' in r)/total, 1)}s\n")
