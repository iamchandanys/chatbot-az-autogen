import requests
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf_from_json(json_data):
    pdf_buffer = io.BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf.setFont("Helvetica", 12)
    
    y_position = letter[1] - 40  # Start position for text
    pdf.drawString(200, y_position, "Insurance Policy Details")
    y_position -= 20
    
    def add_json_to_pdf(pdf, data, y_position, indent=0):
        for key, value in data.items():
            if isinstance(value, dict):
                pdf.drawString(50 + indent, y_position, f"{key}:")
                y_position -= 15
                y_position = add_json_to_pdf(pdf, value, y_position, indent + 20)
            elif isinstance(value, list):
                pdf.drawString(50 + indent, y_position, f"{key}:")
                y_position -= 15
                for item in value:
                    y_position = add_json_to_pdf(pdf, item, y_position, indent + 20)
            else:
                pdf.drawString(50 + indent, y_position, f"{key}: {value}")
                y_position -= 15
        return y_position
    
    add_json_to_pdf(pdf, json_data, y_position)
    pdf.showPage()
    pdf.save()
    pdf_buffer.seek(0)
    return pdf_buffer

def upload_pdf_to_api(pdf_buffer):
    url = "https://emc-b2b-api.azurewebsites.net/api/General/UploadPublicImage"
    files = {'file': ("policy_details.pdf", pdf_buffer, "application/pdf")}
    response = requests.post(url, files=files)
    
    return response.json().get("fileUrl") if response.status_code == 200 else None

def process_and_upload_policy(json_data):
    pdf_buffer = generate_pdf_from_json(json_data)
    return upload_pdf_to_api(pdf_buffer)

if __name__ == "__main__":
    json_data = {
        "policy_number": "POLICY005",
        "policyholder_name": "Robert Davis",
        "vehicle_details": {
            "make": "Nissan",
            "model": "Altima",
            "year": 2022,
            "registration_number": "JKL3456"
        },
        "coverage_details": {
            "type": "Comprehensive",
            "valid_from": "2024-03-20",
            "valid_to": "2025-03-20"
        },
        "claims_history": [
            {
                "claim_id": "CLAIM1003",
                "date_of_incident": "2024-06-18",
                "reason_for_claim": "Hail Damage",
                "status": "Approved"
            }
        ]
    }
    
    uploaded_url = process_and_upload_policy(json_data)
    print("Uploaded File URL:", uploaded_url)