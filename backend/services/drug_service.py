"""
MedEdge — Drug Interaction Service (Offline)
Checks against a local JSON database. No internet required.
"""
import json
import os
from typing import List
from core.logger import logger

# ── Load drug interaction database ────────────────────────────────────────────
_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "drug_interactions.json")

def _load_db() -> dict:
    try:
        with open(_DATA_PATH, "r") as f:
            raw = json.load(f)
        # Convert list-of-2 keys back to tuple keys
        return {tuple(sorted(k)): v for k, v in raw.items()} if isinstance(list(raw.keys())[0], str) else raw
    except Exception:
        return _BUILTIN_DB

# Built-in minimal database (always available even if JSON file missing)
_BUILTIN_DB = {
    ("aspirin", "warfarin"):         {"severity": "HIGH",     "msg": "Increased bleeding risk. Avoid combination or monitor INR closely."},
    ("ibuprofen", "warfarin"):       {"severity": "HIGH",     "msg": "Increased bleeding risk. Avoid combination."},
    ("alcohol", "metformin"):        {"severity": "MODERATE", "msg": "Risk of lactic acidosis. Advise patient to avoid alcohol."},
    ("lisinopril", "potassium"):     {"severity": "MODERATE", "msg": "Risk of hyperkalemia. Monitor potassium levels."},
    ("erythromycin", "simvastatin"): {"severity": "HIGH",     "msg": "Increased risk of myopathy/rhabdomyolysis. Avoid combination."},
    ("antacids", "ciprofloxacin"):   {"severity": "MODERATE", "msg": "Antacids reduce ciprofloxacin absorption. Take 2 hours apart."},
    ("amoxicillin", "warfarin"):     {"severity": "MODERATE", "msg": "May enhance anticoagulant effect. Monitor INR closely."},
    ("alcohol", "metronidazole"):    {"severity": "HIGH",     "msg": "Disulfiram-like reaction: severe nausea/vomiting. Strictly avoid alcohol."},
    ("amiodarone", "digoxin"):       {"severity": "HIGH",     "msg": "Digoxin toxicity risk. Reduce digoxin dose by 50%."},
    ("ssri", "tramadol"):            {"severity": "HIGH",     "msg": "Risk of serotonin syndrome. Monitor closely or avoid."},
    ("clopidogrel", "omeprazole"):   {"severity": "MODERATE", "msg": "Omeprazole may reduce clopidogrel efficacy. Consider pantoprazole instead."},
    ("aspirin", "ibuprofen"):        {"severity": "MODERATE", "msg": "Ibuprofen may reduce aspirin's cardioprotective effect. Take aspirin first."},
    ("levothyroxine", "calcium"):    {"severity": "MODERATE", "msg": "Calcium reduces levothyroxine absorption. Take 4 hours apart."},
    ("quinolones", "antacids"):      {"severity": "MODERATE", "msg": "Antacids chelate quinolones, reducing absorption. Take 2 hours apart."},
}


SEVERITY_ICON = {"HIGH": "🔴", "MODERATE": "🟡", "LOW": "🟢"}


def check_drug_interactions(medications: List[str]) -> str:
    """Check a list of medications against the local offline database."""
    db = _load_db()
    meds_lower = [m.strip().lower() for m in medications if m.strip()]

    if len(meds_lower) < 2:
        return "Only one medication provided — no interaction check needed."

    alerts = []
    checked = set()

    for i, drug1 in enumerate(meds_lower):
        for drug2 in meds_lower[i + 1:]:
            pair = tuple(sorted([drug1, drug2]))
            if pair in checked:
                continue
            checked.add(pair)

            # Exact match
            if pair in _BUILTIN_DB:
                info = _BUILTIN_DB[pair]
                icon = SEVERITY_ICON.get(info["severity"], "⚠️")
                alerts.append(f"{icon} **{drug1.title()} + {drug2.title()}** [{info['severity']}]: {info['msg']}")
                continue

            # Partial match
            for (d1, d2), info in _BUILTIN_DB.items():
                if (d1 in drug1 or drug1 in d1) and (d2 in drug2 or drug2 in d2):
                    pair_key = tuple(sorted([drug1, drug2]))
                    if pair_key not in checked:
                        checked.add(pair_key)
                        icon = SEVERITY_ICON.get(info["severity"], "⚠️")
                        alerts.append(f"{icon} **{drug1.title()} + {drug2.title()}** [{info['severity']}]: {info['msg']}")

    if not alerts:
        return f"✅ No known interactions detected for: {', '.join(m.title() for m in meds_lower)}"

    header = f"⚠️ **{len(alerts)} interaction(s) detected** for {len(meds_lower)} medications:\n\n"
    return header + "\n\n".join(alerts)
