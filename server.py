import json
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "alibayram/medgemma:4b"

# Medical Safety Rule Engine (Deterministic Guardrail)
CONTRAINDICATIONS = {
    "Amiodarone": "Max cumulative dose 450mg in cardiac arrest. Caution in severe sinus node dysfunction.",
    "Calcium": "Do NOT administer routinely in cardiac arrest unless hyperkalemia, hypocalcemia, or CCB overdose is confirmed.",
    "Epi": "Standard dose is 1mg IV/IO every 3-5 minutes. Avoid rapid repeated boluses < 3 minutes."
}

SYSTEM_PROMPT = """You are EchoACLS, an expert emergency resuscitation and critical care physician.
Analyze patient vitals, ECG rhythm, and clinical transcripts to return actionable, evidence-based guidance strictly adhering to ERC/AHA 2025 ACLS algorithms.

Output MUST be strictly valid JSON matching this schema:
{
  "event_type": "DRUG_ADMINISTERED" | "SHOCK_DELIVERED" | "RHYTHM_CHECK" | "VITALS_ALERT" | "ECG_DIAGNOSIS" | "SAFETY_ALERT" | "OTHER",
  "ecg_interpretation": {
    "rhythm": "VFIB" | "PULSELESS_VTACH" | "ASYSTOLE" | "PEA" | "STEMI" | "SINUS_BRADY" | "SVT" | "NSR" | null,
    "rate_bpm": number or null,
    "shockable": boolean
  },
  "clinical_action": "Immediate, step-by-step clinical imperative for the team leader",
  "guideline_citation": "e.g. ERC 2025 Sec 4.1 or NICE CG150",
  "suspected_cause": "Hypovolemia" | "Hypoxia" | "Hydrogen_Ion" | "Hypo_Hyperkalemia" | "Hypothermia" | "Tension_Pneumothorax" | "Tamponade" | "Toxins" | "Thrombosis_Pulmonary" | "Thrombosis_Coronary" | null,
  "drug_recommendation": {
    "drug": string or null,
    "dose": string or null,
    "route": "IV/IO" | null
  },
  "safety_flag": string or null
}
Return ONLY the raw JSON object."""

class ResuscitationInput(BaseModel):
    transcript: Optional[str] = ""
    heart_rate: Optional[int] = None
    ecg_rhythm: Optional[str] = None
    blood_pressure: Optional[str] = None
    spo2: Optional[int] = None

class LogEntry(BaseModel):
    timestamp: str
    event_type: str
    raw_text: str
    suspected_cause: Optional[str] = None
    details: Optional[dict] = None

@app.post("/parse_event")
def parse_event(data: ResuscitationInput):
    context_str = f"Spoken Audio: '{data.transcript}' | HR: {data.heart_rate or 'N/A'} bpm | ECG Rhythm: {data.ecg_rhythm or 'Unspecified'} | BP: {data.blood_pressure or 'N/A'} | SpO2: {data.spo2 or 'N/A'}%"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\n\nClinical Telemetry & Context: \"{context_str}\"\nJSON Output:",
        "format": "json",
        "stream": False
    }
    
    try:
        res = requests.post(OLLAMA_URL, json=payload).json()
        parsed_json = json.loads(res.get("response", "{}"))
    except Exception as e:
        parsed_json = {
            "event_type": "OTHER",
            "ecg_interpretation": {"rhythm": data.ecg_rhythm, "rate_bpm": data.heart_rate, "shockable": False},
            "clinical_action": f"Fallback event logged: {data.transcript}",
            "guideline_citation": "ERC 2025",
            "suspected_cause": None,
            "drug_recommendation": None,
            "safety_flag": None
        }

    # Safety Guardrail Interlock
    for drug_key, warning in CONTRAINDICATIONS.items():
        if drug_key.lower() in (data.transcript or "").lower():
            parsed_json["safety_flag"] = warning

    return parsed_json

@app.post("/export_fhir")
def export_fhir(logs: List[LogEntry]):
    bundle = {
        "resourceType": "Bundle",
        "id": "echo-acls-resuscitation-summary",
        "type": "transaction",
        "meta": {"profile": ["https://fhir.hl7.org.uk/StructureDefinition/UKCore-Bundle"]},
        "entry": []
    }
    for idx, item in enumerate(logs):
        bundle["entry"].append({
            "fullUrl": f"urn:uuid:event-{idx}",
            "resource": {
                "resourceType": "Procedure",
                "status": "completed",
                "code": {
                    "coding": [{"system": "http://snomed.info/sct", "display": item.event_type}]
                },
                "performedDateTime": item.timestamp,
                "note": [{"text": f"{item.raw_text} | Cause: {item.suspected_cause or 'None'}"}]
            }
        })
    return bundle

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
