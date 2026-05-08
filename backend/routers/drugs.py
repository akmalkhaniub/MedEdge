"""
MedEdge — Drug Checker Router
POST /api/v1/drugs/check — Check drug interactions (always offline)
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from core.security import require_api_key
from services.drug_service import check_drug_interactions

router = APIRouter(prefix="/api/v1/drugs", tags=["Drug Interactions"])


class DrugCheckRequest(BaseModel):
    medications: List[str]


@router.post("/check", dependencies=[Depends(require_api_key)])
def drug_check(req: DrugCheckRequest):
    """Check drug interactions from local offline database. No internet required."""
    if not req.medications:
        return {"result": "No medications provided."}
    result = check_drug_interactions(req.medications)
    return {"medications": req.medications, "result": result}
