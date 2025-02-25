import requests
import io
import os
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from dotenv import load_dotenv

load_dotenv()

API_TO_UPLOAD_FILES = os.getenv("api_to_upload_files")

"""
Methods to generate policy details PDF from JSON data and upload it to an API.
"""

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
    url = f"{API_TO_UPLOAD_FILES}"
    files = {'file': ("policy_details.pdf", pdf_buffer, "application/pdf")}
    response = requests.post(url, files=files)
    
    return response.json().get("fileUrl") if response.status_code == 200 else None

def process_and_upload_policy(json_data):
    pdf_buffer = generate_pdf_from_json(json_data)
    return upload_pdf_to_api(pdf_buffer)

"""
Methods to generate invoice PDF from JSON data and upload it to an API.
"""

def generate_invoice(json_data):
    pdf_buffer = io.BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 14)
    
    # Header Section
    pdf.setFillColor(colors.blue)
    pdf.drawString(200, 750, "INVOICE")
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 12)
    
    invoice_data = {
        "invoice_number": f"INV-{random.randint(1000, 9999)}",
        "date": "2025-02-25",
        "customer": json_data.get("policyholder_name", "Unknown"),
        "policy_number": json_data.get("policy_number", "Unknown"),
        "vehicle_details": json_data.get("vehicle_details", {}),
        "coverage_details": json_data.get("coverage_details", {}),
        "items": [
            {"description": "Car Insurance Premium", "amount": random.uniform(100, 500)},
            {"description": "Processing Fee", "amount": random.uniform(10, 50)},
        ],
        "total": 0
    }
    
    invoice_data["total"] = sum(item["amount"] for item in invoice_data["items"])
    
    # Invoice Details
    pdf.drawString(50, 720, f"Invoice Number: {invoice_data['invoice_number']}")
    pdf.drawString(350, 720, f"Date: {invoice_data['date']}")
    pdf.drawString(50, 700, f"Customer: {invoice_data['customer']}")
    pdf.drawString(50, 680, f"Policy Number: {invoice_data['policy_number']}")
    
    y_position = 650
    
    # Vehicle Details
    if invoice_data["vehicle_details"]:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y_position, "Vehicle Details:")
        pdf.setFont("Helvetica", 12)
        y_position -= 20
        for key, value in invoice_data["vehicle_details"].items():
            pdf.drawString(60, y_position, f"{key.capitalize()}: {value}")
            y_position -= 15
    
    # Coverage Details
    if invoice_data["coverage_details"]:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y_position, "Coverage Details:")
        pdf.setFont("Helvetica", 12)
        y_position -= 20
        for key, value in invoice_data["coverage_details"].items():
            pdf.drawString(60, y_position, f"{key.replace('_', ' ').capitalize()}: {value}")
            y_position -= 15
    
    # Items Table
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y_position - 10, "Items:")
    pdf.setFont("Helvetica", 12)
    y_position -= 30
    pdf.line(50, y_position, 550, y_position)
    y_position -= 20
    
    for item in invoice_data["items"]:
        pdf.drawString(60, y_position, f"{item['description']}")
        pdf.drawRightString(500, y_position, f"${item['amount']:.2f}")
        y_position -= 20
    
    pdf.line(50, y_position, 550, y_position)
    y_position -= 30
    
    # Total Amount
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(60, y_position, "Total:")
    pdf.drawRightString(500, y_position, f"${invoice_data['total']:.2f}")
    
    pdf.showPage()
    pdf.save()
    pdf_buffer.seek(0)
    return pdf_buffer

def upload_invoice_to_api(pdf_buffer):
    url = f"{API_TO_UPLOAD_FILES}"
    files = {'file': ("invoice.pdf", pdf_buffer, "application/pdf")}
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        return response.json().get("fileUrl")
    else:
        print("Failed to upload file. Status code:", response.status_code)
        return None

def process_and_upload_invoice(json_data):
    pdf_buffer = generate_invoice(json_data)
    return upload_invoice_to_api(pdf_buffer)


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
    
    uploaded_url = process_and_upload_invoice(json_data)
    print("Uploaded File URL:", uploaded_url)