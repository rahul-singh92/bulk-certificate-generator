import pandas as pd
import uuid
from sqlalchemy.orm import Session
from models import Job, Certificate
from generator import generate_pdf
import os

def process_bulk_generation(job_id: str, file_path: str, db: Session):
    try:
        # Read excel and handle missing empty rows
        df = pd.read_excel(file_path)
    except Exception as e:
        job = db.query(Job).filter(Job.id == job_id).first()
        job.status = f"Failed: Could not read Excel - {str(e)}"
        db.commit()
        return

    for index, row in df.iterrows():
        # Handle missing data gracefully by converting NaNs to empty strings or defaults
        name = str(row.get('name', '')).strip()
        course = str(row.get('course', 'General Event')).strip()
        date = str(row.get('date', '2026-10-07')).split()[0]
        
        # Clean up Pandas 'nan' string if present
        if name.lower() == 'nan': name = ""
        
        cert_record = Certificate(job_id=job_id, recipient_name=name)
        db.add(cert_record)
        db.commit()
        db.refresh(cert_record)
        
        try:
            # Generate unique filename: id_name
            safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
            file_name = f"{cert_record.id}_{safe_name}"
            
            # Map data to generator
            saved_path = generate_pdf(name, course, date, file_name)
            
            # Update success status
            cert_record.status = "Success"
            cert_record.file_path = saved_path
            
        except ValueError as ve:
            # Handle invalid data (e.g. missing name)
            cert_record.status = "Failed"
            cert_record.error_message = str(ve)
        except Exception as e:
            # Handle unexpected library errors
            cert_record.status = "Failed"
            cert_record.error_message = "System error during generation."
            
        db.commit()
    
    # Mark overall job completed
    job = db.query(Job).filter(Job.id == job_id).first()
    job.status = "Completed"
    db.commit()
    
    # Cleanup uploaded temp file
    if os.path.exists(file_path):
        os.remove(file_path)