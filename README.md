# DefensAI - Phishing & AI Content Detection

A complete Full Stack Web Application tailored for OSINT, Cybersecurity, and Machine Learning analysis of images. 
DefensAI analyzes screenshots, emails, and images to detect visual phishing attempts, extract indicators of compromise via OCR, analyze embedded URLs/QR codes, and estimate the probability of the image being AI-generated.

## Features

- **Visual Phishing Detection:** Analyzes text for urgency keywords, credential requests, and more.
- **AI-Generated Content Detection:** Examines EXIF metadata and utilizes image noise variance heuristics.
- **Advanced OCR:** Extracts text, URLs, Emails, and Phone Numbers from images.
- **QR Code Decoder:** Decodes QR codes and analyzes embedded links.
- **Link Analysis (OSINT):** WHOIS lookups, TLD analysis, and domain age verification.
- **Premium UI:** Glassmorphism design, dark mode, responsive layout.
- **Reporting:** Export results in JSON, CSV, or PDF formats.

## Folder Structure

```
pishing osint/
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   └── analyze.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   ├── services/
│   │   ├── ai_detector.py
│   │   ├── link_analyzer.py
│   │   ├── ocr_service.py
│   │   ├── phishing_detector.py
│   │   └── report_generator.py
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js
│   ├── templates/
│   │   ├── index.html
│   │   └── dashboard.html
│   └── main.py
├── uploads/
├── requirements.txt
└── README.md
```

## Installation Instructions

### Prerequisites
1. **Python 3.9+** installed.
2. **Tesseract OCR** must be installed on your system.
   - **Windows:** Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and add the path to your System Environment Variables.
   - **Linux:** `sudo apt-get install tesseract-ocr`
   - **Mac:** `brew install tesseract`

### Setup

1. **Clone/Open the repository.**

2. **Create a Virtual Environment (Optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the Web Interface:**
   Open your browser and navigate to `http://localhost:8000`

6. **Access API Documentation (Swagger):**
   Navigate to `http://localhost:8000/docs`

## Usage
Simply drag and drop an image onto the upload area. The system will process it and return a detailed risk score along with OSINT findings. You can export the results using the buttons provided below the score.
