"""
MedEdge — Clinical Service
Full consultation pipeline using AI service + MedGemma.
All clinical reasoning prompts are here.
"""
import json
from typing import Dict, Any, List, Optional
from services.ai_service import ai_service
from core.logger import logger


# ── SOAP Note Generation ──────────────────────────────────────────────────────
async def generate_soap_note(transcription: str, patient_history: str = "") -> str:
    history_section = f"\n\nPatient History:\n{patient_history}" if patient_history else ""
    prompt = f"""You are an expert clinical documentation specialist.
Based on the consultation transcription below, generate a structured SOAP note.

Transcription:
{transcription}{history_section}

Generate a complete SOAP note with these sections:
**SUBJECTIVE:** (Patient's reported symptoms, HPI, relevant history)
**OBJECTIVE:** (Vital signs, physical exam findings, observable data)
**ASSESSMENT:** (Diagnosis or differential diagnoses with clinical reasoning)
**PLAN:** (Treatment, medications, follow-up, referrals, patient education)

Be concise, professional, and use standard medical terminology.
Output in Markdown format."""

    return await ai_service.complete(prompt, temperature=0.2)


# ── Triage Classification ─────────────────────────────────────────────────────
async def classify_triage(transcription: str, soap_note: str) -> Dict[str, Any]:
    """Uses MedGemma for specialist clinical triage reasoning."""
    prompt = f"""You are a clinical triage specialist.
Based on the consultation below, classify urgency and extract key clinical data.

Transcription: {transcription}
SOAP Note: {soap_note}

Respond ONLY with a valid JSON object:
{{
  "triage_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "triage_color": "green" | "yellow" | "orange" | "red",
  "triage_reasoning": "Brief clinical reasoning (1-2 sentences)",
  "primary_diagnosis": "Most likely diagnosis",
  "medications_mentioned": ["drug1", "drug2"],
  "follow_up_days": 7,
  "immediate_action_required": true | false,
  "red_flags": ["symptom1", "symptom2"],
  "recommended_tests": ["test1", "test2"]
}}"""

    system = "You are MedGemma, a specialized medical AI. Return only valid JSON."
    result = await ai_service.medgemma_complete(prompt, system)

    # Parse JSON
    start = result.find("{")
    end = result.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(result[start:end])
        except json.JSONDecodeError:
            pass

    return {
        "triage_level": "MEDIUM",
        "triage_color": "yellow",
        "triage_reasoning": "Unable to parse triage. Manual review required.",
        "primary_diagnosis": "Unknown",
        "medications_mentioned": [],
        "follow_up_days": 7,
        "immediate_action_required": False,
        "red_flags": [],
        "recommended_tests": [],
    }


# ── Prescription Draft ────────────────────────────────────────────────────────
async def generate_prescription_draft(soap_note: str, triage_data: Dict[str, Any]) -> str:
    """MedGemma generates prescription draft for physician review."""
    diagnosis = triage_data.get("primary_diagnosis", "Unknown")
    prompt = f"""You are a licensed physician. Based on the SOAP note below,
generate a prescription draft for the supervising doctor's review.

Primary Diagnosis: {diagnosis}
SOAP Note: {soap_note}

Format as:
**PRESCRIPTION DRAFT** *(AI-Generated — Physician Review Required)*

**Date:** [Today]
**Diagnosis:** {diagnosis}

| Medication | Dose | Frequency | Duration | Notes |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

**Instructions:** [Dietary, activity, restrictions]
**Follow-up:** [When to return]
**Warnings:** [Important patient warnings]

⚠️ This is an AI-generated draft. Must be reviewed and signed by a licensed physician."""

    system = "You are MedGemma, a specialized clinical prescribing assistant."
    return await ai_service.medgemma_complete(prompt, system)


# ── SMS Summary ────────────────────────────────────────────────────────────────
async def compose_sms_summary(
    soap_note: str,
    triage_data: Dict[str, Any],
    language: str = "English"
) -> str:
    diagnosis = triage_data.get("primary_diagnosis", "your condition")
    follow_up = triage_data.get("follow_up_days", 7)
    is_critical = triage_data.get("triage_level") == "CRITICAL"

    prompt = f"""You are a health communicator writing SMS for a patient with a basic feature phone.
Patient may have limited health literacy. Write in {language}.

SOAP Note: {soap_note}
Diagnosis: {diagnosis}
Follow-up: in {follow_up} days
{"URGENT CASE — Start first SMS with 'URGENT:'" if is_critical else ""}

Rules:
- Maximum 160 characters per SMS (up to 3 messages)
- Use simple, everyday language (no medical jargon)
- Be warm and reassuring
- Include: what was found, what to take/do, when to return
- Format: SMS 1/3, SMS 2/3, SMS 3/3"""

    return await ai_service.complete(prompt, temperature=0.3)


# ── Medical Image Analysis ─────────────────────────────────────────────────────
async def analyze_medical_image(image_path: str, context: str = "") -> str:
    """Analyze wound, rash, X-ray, or vitals chart. Uses MedGemma for interpretation."""
    vision_prompt = """You are an experienced clinical physician analyzing a medical image.

Provide:
1. **Image Type:** (wound, rash, X-ray, vitals chart, lab report, etc.)
2. **Key Findings:** Detailed observations
3. **Clinical Significance:** Medical importance of findings
4. **Recommendations:** Follow-up actions or tests
5. **Urgency:** Is immediate attention required?

Use professional medical language. Be thorough but concise."""

    return await ai_service.vision_complete(image_path, vision_prompt, context)


# ── Wound Progression Comparison ──────────────────────────────────────────────
async def compare_wound_images(image_path_before: str, image_path_after: str) -> str:
    """MedGemma compares two wound images for healing progression."""
    import base64, os

    with open(image_path_before, "rb") as f:
        b64_before = base64.b64encode(f.read()).decode()
    with open(image_path_after, "rb") as f:
        b64_after = base64.b64encode(f.read()).decode()

    from services.settings_service import settings_service
    cfg = settings_service.get_settings()
    from services.ai_service import _OPENAI_AVAILABLE

    prompt = """You are a wound care specialist comparing two wound images.
FIRST image = previous visit. SECOND image = current visit.

Provide wound progression report:
1. **Overall Healing Status:** Healing / Stable / Deteriorating
2. **Size Changes:** Has wound size changed?
3. **Color & Tissue:** Changes in wound bed, granulation, eschar
4. **Infection Signs:** New or resolved infection indicators
5. **Healing Stage:** Current wound healing stage
6. **Recommendations:** Continue / modify treatment / escalate"""

    if not _OPENAI_AVAILABLE:
        return "Vision comparison unavailable. Please ensure the openai package is installed."

    from openai import OpenAI
    from core.config import settings as env_cfg

    if cfg.operation_mode == "offline":
        client = OpenAI(base_url=f"{env_cfg.ollama_base_url}/v1", api_key="ollama")
        model = cfg.ollama_vision_model
    else:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=env_cfg.openrouter_api_key,
        )
        model = cfg.medgemma_model if cfg.use_medgemma else cfg.cloud_model

    import asyncio
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=model,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_before}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_after}"}},
            ]
        }],
        temperature=0.2,
    )
    return response.choices[0].message.content


# ── Vitals OCR ────────────────────────────────────────────────────────────────
async def extract_vitals_from_image(image_path: str) -> str:
    prompt = """You are a clinical data extraction specialist.
Extract all vital signs from this image.

Return structured data:
**Extracted Vitals:**
| Parameter | Value | Unit | Normal Range | Status |
|---|---|---|---|---|
| Blood Pressure | ... | mmHg | 90-120/60-80 | Normal/High/Low |
| Heart Rate | ... | bpm | 60-100 | Normal/High/Low |
| Temperature | ... | °C | 36.1-37.2 | Normal/High/Low |
| SpO2 | ... | % | 95-100 | Normal/Low |
| Respiratory Rate | ... | breaths/min | 12-20 | Normal/High/Low |
| Weight | ... | kg | - | - |
| Height | ... | cm | - | - |

Write "Not recorded" for any value not visible.
Flag any abnormal values with a clinical note."""

    return await ai_service.vision_complete(image_path, prompt)


# ── Document Summarizer ───────────────────────────────────────────────────────
async def summarize_document(image_path: str) -> str:
    prompt = """You are a medical records specialist. Read and summarize this medical document.

Provide:
1. **Document Type:** (Lab report, referral, discharge summary, prescription, etc.)
2. **Date & Patient Info:** (Anonymize if needed)
3. **Key Findings / Results:** Most important clinical information
4. **Abnormal Values:** Anything outside normal ranges (highlight clearly)
5. **Recommendations / Instructions:** Any follow-up actions mentioned
6. **Issuing Physician / Facility:** If visible

Be concise and clinically focused."""

    return await ai_service.vision_complete(image_path, prompt)


# ── Full Consultation Pipeline ────────────────────────────────────────────────
async def run_full_consultation(
    transcription: str,
    patient_history: str = "",
    language: str = "English",
) -> Dict[str, Any]:
    """
    Orchestrate the complete consultation pipeline.
    Returns a dict with all outputs for the API response.
    """
    from services.settings_service import settings_service
    cfg = settings_service.get_settings()

    results: Dict[str, Any] = {"transcription": transcription}

    # Step 1: SOAP Note
    results["soap_note"] = await generate_soap_note(transcription, patient_history)

    # Step 2: Triage (via MedGemma)
    results["triage"] = await classify_triage(transcription, results["soap_note"])

    # Step 3: Drug Interaction Check (always offline — local DB)
    meds = results["triage"].get("medications_mentioned", [])
    if meds and cfg.drug_check_enabled:
        from services.drug_service import check_drug_interactions
        results["drug_interactions"] = check_drug_interactions(meds)
    else:
        results["drug_interactions"] = "No medications detected." if not meds else "Drug check disabled."

    # Step 4: Prescription Draft (via MedGemma)
    if cfg.prescription_draft_enabled:
        results["prescription_draft"] = await generate_prescription_draft(
            results["soap_note"], results["triage"]
        )
    else:
        results["prescription_draft"] = ""

    # Step 5: SMS Summary
    results["sms_summary"] = await compose_sms_summary(
        results["soap_note"], results["triage"], language
    )

    logger.info(
        "consultation_complete",
        triage=results["triage"].get("triage_level"),
        meds_count=len(meds),
        mode=cfg.operation_mode,
    )

    return results
