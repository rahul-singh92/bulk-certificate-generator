import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch

OUTPUT_DIR = "generated_certificates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_pdf(name: str, course: str, date: str, file_name: str) -> str:
    if not name or str(name).strip() == "" or str(name) == "nan":
        raise ValueError("Recipient name is missing.")
        
    file_path = os.path.join(OUTPUT_DIR, f"{file_name}.pdf")
    
    # Create a blank landscape PDF
    c = canvas.Canvas(file_path, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    # Draw Predefined Template Elements
    c.setLineWidth(5)
    c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)
    
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width / 2.0, height - 2.5 * inch, "Certificate of Completion")
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(width / 2.0, height - 3.5 * inch, "This is proudly presented to:")
    
    # Map Dynamic Data
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2.0, height - 4.5 * inch, str(name).title())
    
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2.0, height - 5.5 * inch, f"For successfully completing: {course}")
    
    c.setFont("Helvetica", 12)
    c.drawString(1.5 * inch, 1.5 * inch, f"Date: {date}")
    
    c.save()
    return file_path