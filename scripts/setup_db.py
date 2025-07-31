#!/usr/bin/env python3
"""
Database setup script for BOM Comparison Tool
"""

import os
import sys
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def create_postgres_database():
    """Create PostgreSQL database and tables"""
    
    # Database connection parameters
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'bom_comparison')
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'  # Connect to default database first
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"Database '{DB_NAME}' created successfully!")
        else:
            print(f"Database '{DB_NAME}' already exists.")
        
        cursor.close()
        conn.close()
        
        # Now connect to the new database and create tables
        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
        
        # Create tables
        with engine.connect() as connection:
            # Create comparison_sessions table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS comparison_sessions (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    file1_name VARCHAR(255) NOT NULL,
                    file2_name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'pending',
                    results_file VARCHAR(500)
                )
            """))
            
            # Create comparison_results table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS comparison_results (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    mpn VARCHAR(255) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    file1_data TEXT,
                    file2_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create file_uploads table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS file_uploads (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    original_filename VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_size INTEGER NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id VARCHAR(255)
                )
            """))
            
            # Create error_logs table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS error_logs (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255),
                    error_type VARCHAR(100) NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            connection.commit()
        
        print("Database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'bom_comparison')
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"Connected to PostgreSQL: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == '__main__':
    print("Setting up BOM Comparison Tool database...")
    
    if create_postgres_database():
        print("Database setup completed successfully!")
        
        if test_database_connection():
            print("Database connection test passed!")
        else:
            print("Database connection test failed!")
    else:
        print("Database setup failed!")
        sys.exit(1) 