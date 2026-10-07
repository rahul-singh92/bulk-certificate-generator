from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid
import os
import shutil

from database import engine, Base, get_db
from models import Job, Certificate
from tasks import process_bulk_generation

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/api/jobs")
async def create_generation_job(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")
    
    job_id = str(uuid.uuid4())
    temp_file_path = f"temp_{job_id}.xlsx"
    
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    new_job = Job(id=job_id, status="Processing")
    db.add(new_job)
    db.commit()
    
    # Trigger bulk processing in the background
    background_tasks.add_task(process_bulk_generation, job_id, temp_file_path, db)
    
    return {"job_id": job_id, "message": "Job accepted and is processing in the background."}

@app.get("/api/jobs/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    certificates = db.query(Certificate).filter(Certificate.job_id == job_id).all()
    
    return {
        "job_id": job.id,
        "job_status": job.status,
        "total": len(certificates),
        "successful": sum(1 for c in certificates if c.status == "Success"),
        "failed": sum(1 for c in certificates if c.status == "Failed"),
        "details": [
            {
                "cert_id": c.id, 
                "name": c.recipient_name, 
                "status": c.status, 
                "error": c.error_message
            } for c in certificates
        ]
    }

@app.get("/api/certificates/{cert_id}")
def retrieve_certificate(cert_id: int, db: Session = Depends(get_db)):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate record not found")
    if cert.status != "Success" or not cert.file_path:
        raise HTTPException(status_code=400, detail="Certificate was not generated successfully")
    if not os.path.exists(cert.file_path):
         raise HTTPException(status_code=404, detail="Certificate file missing from server")
         
    return FileResponse(path=cert.file_path, filename=os.path.basename(cert.file_path), media_type='application/pdf')