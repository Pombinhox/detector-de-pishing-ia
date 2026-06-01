import json
import csv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from fastapi.responses import Response, StreamingResponse

class ReportGenerator:
    @staticmethod
    def generate_json(data: dict) -> Response:
        json_data = json.dumps(data, indent=4)
        return Response(content=json_data, media_type="application/json")

    @staticmethod
    def generate_csv(data: dict) -> StreamingResponse:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Flatten dictionary for simple CSV structure
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Risk Score', data.get('risk_score')])
        writer.writerow(['Classification', data.get('classification')])
        writer.writerow(['AI Probability', data.get('ai_probability')])
        writer.writerow(['AI Score', data.get('ai_score')])
        
        reasons_str = "; ".join(data.get('phishing_reasons', []) + data.get('ai_reasons', []))
        writer.writerow(['Reasons', reasons_str])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=report.csv"}
        )

    @staticmethod
    def generate_pdf(data: dict) -> StreamingResponse:
        output = io.BytesIO()
        p = canvas.Canvas(output, pagesize=letter)
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Relatório de Análise de Imagem (OSINT)")
        
        p.setFont("Helvetica", 12)
        y = 700
        
        lines = [
            f"Pontuação de Risco: {data.get('risk_score', 'N/A')}",
            f"Classificação: {data.get('classification', 'N/A')}",
            f"Probabilidade de IA: {data.get('ai_probability', 'N/A')}",
            f"Pontuação IA: {data.get('ai_score', 'N/A')}",
            "",
            "Motivos (Phishing):"
        ]
        
        for reason in data.get('phishing_reasons', []):
            lines.append(f"- {reason}")
            
        lines.append("")
        lines.append("Motivos (IA):")
        for reason in data.get('ai_reasons', []):
            lines.append(f"- {reason}")
            
        for line in lines:
            if y < 50:
                p.showPage()
                y = 750
            p.drawString(100, y, line)
            y -= 20
            
        p.showPage()
        p.save()
        
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=report.pdf"}
        )
