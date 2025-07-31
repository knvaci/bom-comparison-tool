"""
Database models for BOM Comparison Tool
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class ComparisonSession(Base):
    """Model for storing comparison sessions"""
    __tablename__ = 'comparison_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True, nullable=False)
    file1_name = Column(String(255), nullable=False)
    file2_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    results = relationship("ComparisonResult", back_populates="session")

class ComparisonResult(Base):
    """Model for storing comparison results"""
    __tablename__ = 'comparison_results'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('comparison_sessions.id'))
    mpn = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # 'same', 'modified', 'only_in_file1', 'only_in_file2'
    qty1 = Column(String(50))
    qty2 = Column(String(50))
    desc1 = Column(Text)
    desc2 = Column(Text)
    refdes1 = Column(String(255))
    refdes2 = Column(String(255))
    line1 = Column(Integer)
    line2 = Column(Integer)
    session = relationship("ComparisonSession", back_populates="results")

class FileUpload(Base):
    """Model for storing file upload information"""
    __tablename__ = 'file_uploads'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer)
    upload_time = Column(DateTime, default=datetime.utcnow)
    file_type = Column(String(50))

class ErrorLog(Base):
    """Model for storing error logs"""
    __tablename__ = 'error_logs'
    
    id = Column(Integer, primary_key=True)
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String(255)) 