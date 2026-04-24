async def chat_turn(message: str, session_id: str, language: str):
    return {
        "reply": f"Fallback response for {language}: {message}",
        "urgency": 3,
        "differential": [{"code": "R50", "name": "Fever, unspecified"}],
        "red_flags": ["Severe breathing difficulty"],
        "recommended_action": "Consult physician if symptoms worsen.",
    }


async def generate_triage_pdf(_session_data):
    return b""
