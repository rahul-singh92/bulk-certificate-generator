from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, index=True)
    status = Column(String, default="Pending") # Pending, Completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    certificates = relationship("Certificate", back_populates="job")

class Certificate(Base):
    __tablename__ = "certificates"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"))
    recipient_name = Column(String, nullable=True)
    status = Column(String, default="Pending") # Pending, Success, Failed
    error_message = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    
    job = relationship("Job", back_populates="certificates")