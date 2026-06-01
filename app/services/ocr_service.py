import cv2
import pytesseract
from pyzbar.pyzbar import decode
import re

class OCRService:
    @staticmethod
    def extract_text(image_path: str) -> str:
        try:
            # Pytesseract needs the path or an image object
            text = pytesseract.image_to_string(image_path)
            return text
        except pytesseract.TesseractNotFoundError:
            print("Warning: Tesseract OCR is not installed. Text extraction skipped.")
            return ""
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

    @staticmethod
    def extract_entities(text: str) -> dict:
        urls = re.findall(r'(https?://[^\s]+)', text)
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        phones = re.findall(r'\+?[\d\s\-\(\)]{8,15}\d', text) # Simple phone regex
        return {
            "urls": list(set(urls)),
            "emails": list(set(emails)),
            "phones": list(set([p.strip() for p in phones if len(p.strip()) > 7]))
        }

    @staticmethod
    def extract_qr_codes(image_path: str) -> list:
        img = cv2.imread(image_path)
        if img is None:
            return []
        
        decoded_objects = decode(img)
        qr_data = []
        for obj in decoded_objects:
            qr_data.append(obj.data.decode('utf-8'))
        return qr_data

    @staticmethod
    def analyze_image(image_path: str) -> dict:
        text = OCRService.extract_text(image_path)
        entities = OCRService.extract_entities(text)
        qr_codes = OCRService.extract_qr_codes(image_path)
        
        return {
            "raw_text": text,
            "entities": entities,
            "qr_codes": qr_codes
        }
