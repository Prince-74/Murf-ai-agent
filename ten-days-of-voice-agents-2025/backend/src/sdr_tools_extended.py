import json
import os
from datetime import datetime
from typing import Dict, Any
from livekit.agents import function_tool

BASE = os.path.join(os.path.dirname(__file__), "..", "shared-data")
FAQ_PATH = os.path.join(BASE, "company_faq_amazon.json")
LEADS_PATH = os.path.join(BASE, "leads.json")
CAL_PATH = os.path.join(BASE, "calendar.json")
NOTES_PATH = os.path.join(BASE, "notes.json")
EMAILS_PATH = os.path.join(BASE, "followups.json")


def _read(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception:
        return {}


def _write(path: str, data: Any):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


# --------- FAQ & search -----------
@function_tool
async def find_faq_answer(query: str):
    data = _read(FAQ_PATH) or {}
    # direct question match (simple)
    for item in data.get("faq", []):
        q = item.get("question", "").lower()
        if any(token in query.lower() for token in q.split()[:4]):
            return item.get("answer")
    # fallback keyword search
    for item in data.get("faq", []):
        combined = (item.get("question", "") + " " + item.get("answer", "")).lower()
        if any(word in query.lower() for word in combined.split()):
            return item.get("answer")
    return "Sorry, I don't have a direct answer in the FAQ. I can connect you to a representative if you'd like."


# ------- Lead collection ----------
@function_tool
async def collect_lead_field(field: str, value: str):
    leads = _read(LEADS_PATH) or []
    if not isinstance(leads, list):
        leads = []
    if not leads or leads[-1].get("complete"):
        leads.append({"created_at": datetime.utcnow().isoformat()})
    leads[-1][field] = value
    _write(LEADS_PATH, leads)
    return {"status": "saved", field: value}


@function_tool
async def finalize_lead():
    leads = _read(LEADS_PATH) or []
    if not leads:
        return {"error": "no_active_lead"}
    lead = leads[-1]
    lead["complete"] = True
    lead["finalized_at"] = datetime.utcnow().isoformat()
    _write(LEADS_PATH, leads)
    # create CRM note
    note = {
        "lead_summary": lead,
        "generated_at": datetime.utcnow().isoformat()
    }
    notes = _read(NOTES_PATH) or []
    notes.append(note)
    _write(NOTES_PATH, notes)
    return {"summary": lead}


# ------- Mock meeting scheduler ----------
@function_tool
async def list_slots():
    cal = _read(CAL_PATH) or {}
    return {"available_slots": cal.get("available_slots", [])}


@function_tool
async def book_slot(slot_iso: str, name: str = "", email: str = ""):
    cal = _read(CAL_PATH) or {"available_slots": [], "bookings": []}
    if slot_iso not in cal.get("available_slots", []):
        return {"error": "slot_unavailable"}
    booking = {
        "slot": slot_iso,
        "name": name,
        "email": email,
        "booked_at": datetime.utcnow().isoformat()
    }
    cal.setdefault("bookings", []).append(booking)
    cal["available_slots"].remove(slot_iso)
    _write(CAL_PATH, cal)
    return {"booked": booking}


# ------ CRM notes / qualification ------
@function_tool
async def generate_crm_notes():
    leads = _read(LEADS_PATH) or []
    if not leads:
        return {"error": "no_leads"}
    lead = leads[-1]
    # simple heuristics
    pain = []
    if "problem" in lead.get("use_case", "").lower():
        pain.append("explicit problem mentioned")
    budget = "budget" in (lead.get("use_case", "") + lead.get("timeline", "")).lower()
    decision_maker = "founder" in (lead.get("role", "")).lower() or "ceo" in (lead.get("role", "")).lower()
    clarity = 80 if lead.get("timeline", "").lower() in ["now", "soon"] else 50
    score = int((clarity) * (1.2 if decision_maker else 1.0))
    note = {
        "lead": lead,
        "pain_points": pain,
        "budget_mentioned": budget,
        "decision_maker": decision_maker,
        "clarity_score": clarity,
        "fit_score": min(score, 100),
        "generated_at": datetime.utcnow().isoformat()
    }
    notes = _read(NOTES_PATH) or []
    notes.append(note)
    _write(NOTES_PATH, notes)
    return {"note": note}


# ------- Persona inference ----------
@function_tool
async def infer_persona(text: str):
    low = (text or "").lower()
    if any(w in low for w in ["api", "developer", "integration", "sdk", "engineer"]):
        return {"persona": "developer"}
    if any(w in low for w in ["product", "pm", "product manager", "roadmap"]):
        return {"persona": "product_manager"}
    if any(w in low for w in ["founder", "ceo", "co-founder"]):
        return {"persona": "founder"}
    return {"persona": "unknown"}


# ------- Follow-up email draft ----------
@function_tool
async def draft_followup_email():
    leads = _read(LEADS_PATH) or []
    if not leads:
        return {"error": "no_leads"}
    lead = leads[-1]
    subject = f"Follow-up: {lead.get('name','')} — next steps with Amazon solutions"
    body = (f"Hi {lead.get('name','')},\n\nThanks for the chat today. From our conversation, your key needs are: "
            f"{lead.get('use_case','N/A')}. We agreed to the following timeline: {lead.get('timeline','N/A')}.\n\n"
            "If you'd like, we can confirm a demo time. Looking forward to following up.\n\nBest,\nSDR Team")
    emails = _read(EMAILS_PATH) or []
    emails.append({"subject": subject, "body": body, "created_at": datetime.utcnow().isoformat()})
    _write(EMAILS_PATH, emails)
    return {"subject": subject, "body": body}


# ------- Return visitor recognition ----------
@function_tool
async def find_returning(email_or_name: str):
    leads = _read(LEADS_PATH) or []
    for lead in reversed(leads):
        if (lead.get("email", "") or "").lower() == (email_or_name or "").lower() or \
           (lead.get("name", "") or "").lower() == (email_or_name or "").lower():
            return {"returning": True, "last_lead": lead}
    return {"returning": False}
