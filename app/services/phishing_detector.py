from app.services.ocr_service import OCRService
from app.services.link_analyzer import LinkAnalyzer

class PhishingDetector:
    PHISHING_KEYWORDS = [
        "urgent", "verify your account", "suspend", "password", "login", 
        "click here", "update your information", "bank account", 
        "security alert", "unauthorized login", "action required",
        "urgente", "verifique sua conta", "suspender", "senha", "entrar",
        "clique aqui", "atualize suas informações", "conta bancária",
        "alerta de segurança", "login não autorizado", "ação necessária"
    ]

    @staticmethod
    def analyze(image_path: str) -> dict:
        ocr_result = OCRService.analyze_image(image_path)
        text_lower = ocr_result["raw_text"].lower()
        
        score = 0
        reasons = []
        
        # 1. Keyword Analysis
        found_keywords = [kw for kw in PhishingDetector.PHISHING_KEYWORDS if kw in text_lower]
        if found_keywords:
            score += min(len(found_keywords) * 15, 50)
            reasons.append(f"Found suspicious keywords: {', '.join(found_keywords)}")

        # 2. URL Analysis
        urls = ocr_result["entities"].get("urls", [])
        if urls:
            highest_url_score = 0
            for url in urls:
                url_analysis = LinkAnalyzer.analyze_url(url)
                if url_analysis["risk_score"] > highest_url_score:
                    highest_url_score = url_analysis["risk_score"]
                    if url_analysis["reasons"]:
                        reasons.extend([f"URL ({url}): {r}" for r in url_analysis["reasons"]])
            
            score += highest_url_score * 0.5 # URLs contribute up to 50 points
            
        # 3. QR Code Analysis
        qr_codes = ocr_result.get("qr_codes", [])
        if qr_codes:
            for qr in qr_codes:
                if qr.startswith("http"):
                    qr_analysis = LinkAnalyzer.analyze_url(qr)
                    score += qr_analysis["risk_score"] * 0.5
                    if qr_analysis["reasons"]:
                        reasons.extend([f"QR Link ({qr}): {r}" for r in qr_analysis["reasons"]])
                else:
                    reasons.append("Contains non-URL QR code data.")

        score = min(score, 100)
        
        classification = "Seguro"
        if score > 70:
            classification = "Alto Risco"
        elif score > 30:
            classification = "Suspeito"

        return {
            "risk_score": score,
            "classification": classification,
            "reasons": list(set(reasons)), # deduplicate
            "extracted_text": ocr_result["raw_text"],
            "urls_found": urls,
            "qr_codes_found": qr_codes
        }
