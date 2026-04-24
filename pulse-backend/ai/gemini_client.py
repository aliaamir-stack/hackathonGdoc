async def identify_medicine(_image_base64: str):
    return {"drug_name": "Paracetamol", "dosage": "500mg", "expiry": "2027-03-30"}


async def match_emergency_protocol(_transcription: str):
    return {
        "protocol": "CPR Adult",
        "steps": ["Call ambulance", "Begin chest compressions"],
        "call_ambulance": True,
        "matched_confidence": 0.9,
    }
