import whois
from urllib.parse import urlparse
import datetime

class LinkAnalyzer:
    SUSPICIOUS_TLDS = ['.xyz', '.top', '.club', '.online', '.site', '.click', '.tk', '.ml']
    
    @staticmethod
    def extract_domain(url: str) -> str:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return ""

    @staticmethod
    def analyze_domain(domain: str) -> dict:
        if not domain:
            return {"error": "Invalid domain"}
        
        score = 0
        reasons = []
        
        # Check TLD
        if any(domain.endswith(tld) for tld in LinkAnalyzer.SUSPICIOUS_TLDS):
            score += 30
            reasons.append("Suspicious TLD")
            
        # Check whois
        try:
            w = whois.whois(domain)
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
                
            if creation_date:
                age_days = (datetime.datetime.now() - creation_date).days
                if age_days < 30:
                    score += 50
                    reasons.append("Domain is less than 30 days old")
                elif age_days < 180:
                    score += 20
                    reasons.append("Domain is relatively new (less than 6 months)")
            else:
                score += 10
                reasons.append("Could not determine domain age")
                
        except Exception as e:
            score += 20
            reasons.append("WHOIS lookup failed or domain not found")

        # Clamp score
        score = min(score, 100)
        
        classification = "Seguro"
        if score > 70:
            classification = "Alto Risco"
        elif score > 30:
            classification = "Suspeito"
            
        return {
            "domain": domain,
            "risk_score": score,
            "classification": classification,
            "reasons": reasons
        }

    @staticmethod
    def analyze_url(url: str) -> dict:
        domain = LinkAnalyzer.extract_domain(url)
        return LinkAnalyzer.analyze_domain(domain)
