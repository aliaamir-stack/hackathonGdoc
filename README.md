## Village Health AI

**Team:** Kaali Aandhi (Ali Aamir, Arsal, Mikail, Xajnan, Ammar)
**Theme & Challenge:** Theme 1 — AI-Powered Rural Health Diagnostic Assistant
**Track:** Hard

---

### Problem statement

Over 60% of Pakistan's population lives in rural areas where access to qualified doctors is severely limited. Community health workers (Lady Health Workers) lack the clinical training to triage complex symptoms, leading to delayed referrals, misdiagnoses, and preventable deaths. Language barriers compound the problem — patients speak Urdu, Sindhi, Pashto, or Punjabi, while medical systems operate in English.

Village Health AI solves this by enabling a health worker to simply record the patient speaking about their symptoms in their native language. The system transcribes, translates, triages, cross-references medical guidelines, checks for life-threatening red flags, and generates a bilingual referral note — all in under 30 seconds.

### Why multi-agent?

A single LLM cannot reliably perform medical triage. Each clinical step requires specialized reasoning with different context, safety constraints, and failure modes:

- **Transcription** needs audio-specific ASR models (Whisper), not text LLMs
- **Localization** requires faithful medical translation without hallucinating symptoms
- **Triage** must follow strict severity protocols (critical/high/medium/low) and flag missing info
- **Specialist analysis** needs RAG retrieval from WHO/CDC guidelines — not LLM memory
- **Safety override** must independently verify red flags (chest pain, stroke signs, sepsis) and can force-escalate the pipeline regardless of triage severity
- **Summary generation** must produce both a clinical English note for the doctor AND a back-translated note the patient can understand

Each agent has a single responsibility, auditable output, and can fail gracefully without bringing down the entire pipeline. The Safety Agent acts as an independent observer that can override all upstream decisions — this separation of concerns is impossible with a single-agent approach.

### Agent architecture

| Agent | Role | Model | Key Output |
|-------|------|-------|------------|
| Transcribe | Whisper ASR — converts patient audio to text | Groq Whisper | `raw_transcript` |
| Localize | Translates native language to clinical English | Llama 3.1-8B (Groq) | `clinical_english`, `source_language` |
| Triage | Extracts symptoms, assigns severity (0-10), flags missing clinical info | Llama 3.3-70B (Groq) | `symptoms[]`, `severity`, `missing_info[]` |
| Specialist | RAG cross-reference against WHO/CDC medical guidelines via FAISS | Llama 3.3-70B (Groq) + FAISS | `potential_conditions[]`, `urgency_level` (1-5) |
| Safety | Independent red-flag detection — can force URGENT override | Llama 3.3-70B (Groq) | `is_urgent`, `red_flags[]`, `override_required` |
| Summary | Generates bilingual referral note (English + patient's language) | Llama 3.3-70B (Groq) | `referral_note_en`, `referral_note_native` |

**Pipeline flow:**

```
Audio/Text → FastAPI → Transcribe → Localize → Triage → Specialist → Safety → [Router] → Summary → PipelineResponse
                                                                         ↓
                                                                  override_required?
                                                                   YES → URGENT Summary
                                                                   NO  → Normal Summary
```

The pipeline is orchestrated by **LangGraph** with a shared **PipelineState** (Pydantic v2) that every agent reads from and writes to. A conditional router after the Safety Agent determines the urgency pathway.

### How to run

**Prerequisites:** Python 3.11+, a Groq API key ([console.groq.com](https://console.groq.com))

```bash
# Clone the repo
git clone https://github.com/aliaamir-stack/HackaThon-Kaali-Aandhi.git
cd HackaThon-Kaali-Aandhi

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
# Create backend/.env with:
#   GROQ_API_KEY=your_key_here
#   GROQ_MODEL=llama-3.3-70b-versatile

# Build the FAISS knowledge base (one-time)
python -m backend.knowledge_base.ingest

# Start the server
uvicorn backend.main:app --reload --port 8000
```

API docs available at [http://localhost:8000/docs](http://localhost:8000/docs)

**Frontend (Next.js):**

```bash
cd FrontendExternal
npm install
# Set NEXT_PUBLIC_API_URL=http://localhost:8000 in .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Demo


- [Demo video & architecture diagram] ::
  https://drive.google.com/drive/folders/1XX00TGHHttdE1H5vQlFzA7fqSNXHHdwM?usp=sharing

### Tech stack

| Layer | Technology |
|-------|-----------|
| Orchestration | LangGraph (StateGraph with conditional routing) |
| LLM Provider | Groq (Whisper, Llama 3.1-8B, Llama 3.3-70B) |
| Backend | Python 3.11, FastAPI, Pydantic v2, Uvicorn |
| RAG | FAISS vector store, HuggingFace Embeddings (all-MiniLM-L6-v2), PyPDF |
| Frontend | Next.js, TypeScript, Tailwind CSS, Framer Motion |
| Deployment | Railway (backend), Vercel (frontend) |
| Languages supported | Urdu, Sindhi, Pashto, Punjabi, English |

### Repository structure

```
HackaThon-Kaali-Aandhi/
├── backend/
│   ├── agents/              # 5 LLM-powered agents
│   ├── pipeline/            # LangGraph state machine + router
│   ├── prompts/             # System prompts for each agent
│   ├── tools/               # Whisper transcriber + FAISS retriever
│   ├── knowledge_base/      # PDF ingestion + FAISS index
│   └── main.py              # FastAPI entry point
├── FrontendExternal/        # Next.js frontend (Ammar)
│   └── src/
│       ├── app/             # Pages (home, analyze, results)
│       ├── components/      # Pipeline UI, dashboard, inputs
│       └── lib/             # API client, types, coercion
├── frontend/src/types/      # Shared TypeScript type definitions
├── data/                    # Medical guideline PDFs for RAG
├── Procfile                 # Railway deployment
├── requirements.txt         # Python dependencies
└── runtime.txt              # Python version spec
```
