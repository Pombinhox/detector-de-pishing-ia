from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import shutil
import os
import json
import numpy as np
from app.db.database import get_db
from app.db.models import AnalysisResult
from app.services.phishing_detector import PhishingDetector
from app.services.ai_detector import AIDetector
from app.services.report_generator import ReportGenerator

router = APIRouter()

# ── Encoder seguro para tipos numpy ──────────────────────────────────────────
class NumpySafeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/image")
async def analyze_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Run analysis
    phishing_result = PhishingDetector.analyze(file_path)
    ai_result = AIDetector.analyze(file_path)
    
    final_score = max(phishing_result["risk_score"], ai_result["ai_score"])
    classification = "Seguro"
    if final_score > 70:
        classification = "Alto Risco"
    elif final_score > 30:
        classification = "Suspeito"
        
    combined_result = {
        "risk_score": final_score,
        "classification": classification,
        "ai_probability": ai_result["ai_probability"],
        "ai_score": ai_result["ai_score"],
        "phishing_reasons": phishing_result["reasons"],
        "ai_reasons": ai_result["reasons"],
        "hidden_codes": ai_result.get("hidden_codes", []),
        "extracted_text": phishing_result["extracted_text"],
        "urls_found": phishing_result["urls_found"],
        "qr_codes_found": phishing_result["qr_codes_found"],
        "metadata_software": ai_result["metadata_software"],
        "statistical_analysis": ai_result.get("statistical_analysis", {})
    }
    
    # Save to DB
    db_result = AnalysisResult(
        filename=file.filename,
        analysis_type="image",
        risk_score=final_score,
        classification=classification,
        ai_probability=ai_result["ai_probability"],
        detailed_report=json.dumps(combined_result)
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    combined_result["id"] = db_result.id
    return combined_result

@router.get("/report/{analysis_id}")
async def get_report(analysis_id: int, format: str = Query("json"), db: Session = Depends(get_db)):
    result = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    data = json.loads(result.detailed_report)
    
    if format == "pdf":
        return ReportGenerator.generate_pdf(data)
    elif format == "csv":
        return ReportGenerator.generate_csv(data)
    else:
        return ReportGenerator.generate_json(data)
