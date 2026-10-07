import pytest
from fastapi.testclient import TestClient
import pandas as pd
import io
from main import app

# Initialize the test client
client = TestClient(app)

def create_dummy_excel(data):
    """Helper function to create an Excel file in memory for testing"""
    df = pd.DataFrame(data)
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False, engine='openpyxl')
    excel_file.seek(0)
    return excel_file

def test_invalid_file_type():
    """Test that uploading a non-Excel file is rejected (Input Validation)"""
    response = client.post(
        "/api/jobs", 
        files={"file": ("test.txt", b"dummy text content", "text/plain")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file type. Please upload an Excel file."

def test_full_certificate_generation_flow():
    """Test job creation, failure handling, status checking, and retrieval"""
    # Create test data: One valid row, one invalid row (missing name)
    data = {
        "name": ["Test User", ""],
        "course": ["FastAPI Testing", "FastAPI Testing"],
        "date": ["2026-10-08", "2026-10-08"]
    }
    excel_file = create_dummy_excel(data)
    
    # 1. Test Creating a generation job
    upload_response = client.post(
        "/api/jobs", 
        files={"file": ("recipients.xlsx", excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert upload_response.status_code == 200
    job_id = upload_response.json()["job_id"]
    assert job_id is not None

    # 2. Test Job status/progress & Handling an individual certificate failure
    status_response = client.get(f"/api/jobs/{job_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    
    assert status_data["total"] == 2
    assert status_data["successful"] == 1
    assert status_data["failed"] == 1 # Validates that missing name was caught
    
    # 3. Test Retrieving generated certificates
    # Find the ID of the successful certificate
    successful_cert = next(cert for cert in status_data["details"] if cert["status"] == "Success")
    cert_id = successful_cert["cert_id"]
    
    retrieve_response = client.get(f"/api/certificates/{cert_id}")
    assert retrieve_response.status_code == 200
    assert retrieve_response.headers["content-type"] == "application/pdf"