"""
MedEdge — Imaging Router
POST /api/v1/imaging/analyze       — Single image analysis
POST /api/v1/imaging/wound-tracker — Compare two wound images
POST /api/v1/imaging/vitals-ocr    — Extract vitals from image
POST /api/v1/imaging/summarize-doc — Summarize medical document
"""
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from core.security import require_api_key
from services.clinical_service import (
    analyze_medical_image,
    compare_wound_images,
    extract_vitals_from_image,
    summarize_document,
)

router = APIRouter(prefix="/api/v1/imaging", tags=["Medical Imaging"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _save_upload(upload: UploadFile) -> str:
    ext = os.path.splitext(upload.filename)[1].lower() or ".jpg"
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported image format: {ext}")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    return tmp.name


@router.post("/analyze", dependencies=[Depends(require_api_key)])
async def analyze_image(
    image: UploadFile = File(...),
    context: str = Form(default=""),
):
    """Analyze any medical image: wound, rash, X-ray, skin condition, or monitor."""
    ext = os.path.splitext(image.filename)[1].lower() or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await image.read())
        tmp_path = tmp.name
    try:
        result = await analyze_medical_image(tmp_path, context)
        return {"analysis": result}
    finally:
        os.unlink(tmp_path)


@router.post("/wound-tracker", dependencies=[Depends(require_api_key)])
async def wound_tracker(
    image_before: UploadFile = File(...),
    image_after: UploadFile = File(...),
):
    """Compare two wound images to assess healing progression."""
    ext_b = os.path.splitext(image_before.filename)[1].lower() or ".jpg"
    ext_a = os.path.splitext(image_after.filename)[1].lower() or ".jpg"

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext_b) as tmp_b:
        tmp_b.write(await image_before.read())
        path_b = tmp_b.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext_a) as tmp_a:
        tmp_a.write(await image_after.read())
        path_a = tmp_a.name

    try:
        result = await compare_wound_images(path_b, path_a)
        return {"progression_report": result}
    finally:
        os.unlink(path_b)
        os.unlink(path_a)


@router.post("/vitals-ocr", dependencies=[Depends(require_api_key)])
async def vitals_ocr(image: UploadFile = File(...)):
    """Extract structured vital signs from a photo of a vitals chart or monitor."""
    ext = os.path.splitext(image.filename)[1].lower() or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await image.read())
        tmp_path = tmp.name
    try:
        result = await extract_vitals_from_image(tmp_path)
        return {"vitals": result}
    finally:
        os.unlink(tmp_path)


@router.post("/summarize-doc", dependencies=[Depends(require_api_key)])
async def summarize_doc(image: UploadFile = File(...)):
    """Summarize a medical document: lab report, referral, discharge summary."""
    ext = os.path.splitext(image.filename)[1].lower() or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await image.read())
        tmp_path = tmp.name
    try:
        result = await summarize_document(tmp_path)
        return {"summary": result}
    finally:
        os.unlink(tmp_path)
