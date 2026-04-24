"""
PULSE Symptom Navigator Engine + PDF Generator
M3 — AI/ML Engineer
"""

import os
import io
import json
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .gemini_client import gemini
from .prompts import SYMPTOM_NAVIGATOR_SYSTEM_PROMPT

load_dotenv()


# ── Pydantic Models ──────────────────────────────────────────────────────────

class DifferentialDiagnosis(BaseModel):
    icd10_code: str
    condition: str
    likelihood: str  # "High" | "Medium" | "Low"


class SymptomTriageResult(BaseModel):
    urgency: int = Field(..., ge=1, le=5)
    urgency_label: str
    differential: list[DifferentialDiagnosis]
    red_flags: list[str]
    recommended_action: str
    follow_up_needed: bool
    patient_summary: str
    ready_for_triage: bool = True


# ── Symptom Navigator Class ──────────────────────────────────────────────────

class SymptomNavigator:
    """
    Multi-turn clinical triage chatbot.

    Usage:
        nav = SymptomNavigator(session_id="user-123")
        reply = nav.chat("I have a fever and joint pain")
        # ... continue conversation ...
        result = nav.get_triage_result()  # returns SymptomTriageResult
    """

    MAX_TURNS = 4

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: list[dict] = []  # {"role": "user"|"model", "content": str}
        self.triage_result: Optional[SymptomTriageResult] = None
        self.turn_count = 0
        self.language = "english"

    def chat(self, user_message: str) -> dict:
        """
        Sends a user message and returns the model's response.
        Returns: {"reply": str, "ready": bool, "triage": dict|None}
        """
        self.turn_count += 1

        # Detect language on first message
        if self.turn_count == 1:
            self.language = gemini.detect_language(user_message)

        self.history.append({"role": "user", "content": user_message})

        # Build conversation context for Gemini
        conversation_text = self._build_conversation()

        # Force triage output after MAX_TURNS
        force_triage = self.turn_count >= self.MAX_TURNS
        if force_triage:
            conversation_text += "\n\n[SYSTEM: Enough information gathered. Now produce the JSON triage result.]"

        try:
            raw_response = gemini.generate(
                prompt=conversation_text,
                system_prompt=SYMPTOM_NAVIGATOR_SYSTEM_PROMPT,
                temperature=0.4,
            )
        except Exception as e:
            raw_response = "I'm sorry, I'm having trouble connecting right now. Please try again."

        # Check if response contains triage JSON
        triage_data = self._extract_triage(raw_response)

        if triage_data and triage_data.get("ready_for_triage"):
            try:
                # Validate via Pydantic
                self.triage_result = SymptomTriageResult(**triage_data)
                reply_text = self._format_triage_reply(self.triage_result)
            except Exception:
                reply_text = raw_response
                self.triage_result = None
        else:
            reply_text = raw_response

        self.history.append({"role": "model", "content": reply_text})

        return {
            "session_id": self.session_id,
            "reply": reply_text,
            "ready": self.triage_result is not None,
            "triage": self.triage_result.model_dump() if self.triage_result else None,
            "turn": self.turn_count,
            "language": self.language,
        }

    def get_triage_result(self) -> Optional[SymptomTriageResult]:
        return self.triage_result

    def _build_conversation(self) -> str:
        lines = []
        for msg in self.history:
            role = "Patient" if msg["role"] == "user" else "Navigator"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    def _extract_triage(self, text: str) -> Optional[dict]:
        """Try to parse a JSON triage block from the model's response."""
        import re
        match = re.search(r'\{.*"ready_for_triage".*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return None

    def _format_triage_reply(self, result: SymptomTriageResult) -> str:
        urgency_emoji = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🚨"}.get(result.urgency, "⚪")
        conditions = ", ".join([d.condition for d in result.differential[:3]])
        flags = "\n".join([f"  ⚠️ {f}" for f in result.red_flags]) if result.red_flags else "  None identified"
        return (
            f"{urgency_emoji} **Urgency Level {result.urgency} — {result.urgency_label}**\n\n"
            f"**Possible conditions:** {conditions}\n\n"
            f"**Red flags:**\n{flags}\n\n"
            f"**Recommended action:** {result.recommended_action}\n\n"
            f"A triage report has been generated that you can download and show to your doctor."
        )


# ── PDF Generator ────────────────────────────────────────────────────────────

def generate_triage_pdf(session_data: dict) -> bytes:
    """
    Generates a downloadable triage PDF from session data.

    Args:
        session_data: dict containing triage result + conversation history

    Returns:
        bytes: PDF file content
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    story = []

    # ── Header ─────────────────────────────────────────────────────────────
    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=22,
                                  textColor=colors.HexColor("#00e87a"), spaceAfter=4)
    subtitle_style = ParagraphStyle("sub", parent=styles["Normal"], fontSize=10,
                                     textColor=colors.HexColor("#8496aa"), spaceAfter=12)

    story.append(Paragraph("PULSE Health Intelligence", title_style))
    story.append(Paragraph("Symptom Triage Report — For Patient Use Only", subtitle_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a2535")))
    story.append(Spacer(1, 8*mm))

    triage = session_data.get("triage", {})
    urgency = triage.get("urgency", 1)
    urgency_label = triage.get("urgency_label", "Routine")

    # Urgency color
    urgency_color = {1: "#00e87a", 2: "#ffb347", 3: "#ff9800", 4: "#ff4d6a", 5: "#cc0000"}.get(urgency, "#888")

    urgency_style = ParagraphStyle("urgency", parent=styles["Heading1"], fontSize=16,
                                    textColor=colors.HexColor(urgency_color), spaceAfter=4)
    story.append(Paragraph(f"Urgency: Level {urgency} — {urgency_label}", urgency_style))
    story.append(Spacer(1, 4*mm))

    # ── Patient Summary ─────────────────────────────────────────────────────
    heading_style = ParagraphStyle("heading", parent=styles["Heading2"], fontSize=12,
                                    textColor=colors.HexColor("#dce8f0"), spaceAfter=4)
    body_style = ParagraphStyle("body", parent=styles["Normal"], fontSize=10,
                                 textColor=colors.HexColor("#8496aa"), spaceAfter=8, leading=16)

    story.append(Paragraph("Patient Summary", heading_style))
    story.append(Paragraph(triage.get("patient_summary", "N/A"), body_style))
    story.append(Spacer(1, 4*mm))

    # ── Recommended Action ──────────────────────────────────────────────────
    story.append(Paragraph("Recommended Action", heading_style))
    story.append(Paragraph(triage.get("recommended_action", "Please consult a doctor."), body_style))
    story.append(Spacer(1, 4*mm))

    # ── Differential Diagnoses ──────────────────────────────────────────────
    differential = triage.get("differential", [])
    if differential:
        story.append(Paragraph("Possible Conditions (Differential)", heading_style))
        table_data = [["ICD-10 Code", "Condition", "Likelihood"]]
        for d in differential:
            table_data.append([d.get("icd10_code", ""), d.get("condition", ""), d.get("likelihood", "")])

        table = Table(table_data, colWidths=[40*mm, 90*mm, 30*mm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#131c24")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#00e87a")),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#dce8f0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#0d1318"), colors.HexColor("#131c24")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1a2535")),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(table)
        story.append(Spacer(1, 4*mm))

    # ── Red Flags ───────────────────────────────────────────────────────────
    red_flags = triage.get("red_flags", [])
    if red_flags:
        story.append(Paragraph("⚠️ Red Flags (Report to Doctor Immediately)", heading_style))
        for flag in red_flags:
            story.append(Paragraph(f"• {flag}", body_style))
        story.append(Spacer(1, 4*mm))

    # ── Disclaimer ──────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a2535")))
    story.append(Spacer(1, 4*mm))
    disclaimer_style = ParagraphStyle("disc", parent=styles["Normal"], fontSize=8,
                                       textColor=colors.HexColor("#4a6070"), leading=12)
    story.append(Paragraph(
        "DISCLAIMER: This report is generated by an AI triage assistant and is NOT a medical diagnosis. "
        "It is intended to guide you to appropriate care. Always consult a qualified medical professional. "
        "In case of emergency (Urgency 4-5), call emergency services immediately.",
        disclaimer_style,
    ))

    doc.build(story)
    return buffer.getvalue()
