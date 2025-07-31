#!/usr/bin/env python3
"""
Docker PostgreSQL setup script for BOM Comparison Tool
Handles authentication and container setup
"""

import os
import sys
import subprocess
import time
import psycopg2

def check_docker():
    """Check if Docker is running"""
    try:
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def pull_image_with_auth():
    """Pull PostgreSQL image with authentication handling"""
    print("🐳 Pulling PostgreSQL image...")
    
    # Try different approaches to pull the image
    approaches = [
        # Try without authentication first
        ['docker', 'pull', 'postgres:15-alpine'],
        # Try with different registry
        ['docker', 'pull', 'library/postgres:15-alpine'],
        # Try with explicit registry
        ['docker', 'pull', 'docker.io/library/postgres:15-alpine']
    ]
    
    for i, cmd in enumerate(approaches):
        print(f"Attempt {i+1}: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Image pulled successfully!")
                return True
            else:
                print(f"❌ Failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("❌ All pull attempts failed")
    return False

def start_container():
    """Start PostgreSQL container"""
    print("🚀 Starting PostgreSQL container...")
    
    try:
        # Stop any existing container
        subprocess.run(['docker-compose', 'down'], capture_output=True)
        
        # Start the container
        result = subprocess.run(['docker-compose', 'up', '-d'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Container started successfully!")
            return True
        else:
            print(f"❌ Failed to start container: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error starting container: {e}")
        return False

def wait_for_postgres():
    """Wait for PostgreSQL to be ready"""
    print("⏳ Waiting for PostgreSQL to be ready...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                user='postgres',
                password='Letmein_123',
                database='bom_comparison'
            )
            conn.close()
            print("✅ PostgreSQL is ready!")
            return True
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"⏳ Attempt {attempt + 1}/{max_attempts}: Waiting...")
                time.sleep(3)
            else:
                print(f"❌ PostgreSQL not ready after {max_attempts} attempts")
                return False
    
    return False

def setup_database_tables():
    """Set up database tables"""
    print("🗄️ Setting up database tables...")
    
    # Set environment variables
    os.environ.update({
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_USER': 'postgres',
        'DB_PASSWORD': 'Letmein_123',
        'DB_NAME': 'bom_comparison',
        'DATABASE_URL': 'postgresql://postgres:Letmein_123@localhost:5432/bom_comparison'
    })
    
    try:
        from scripts.setup_db import create_postgres_database
        if create_postgres_database():
            print("✅ Database tables created successfully!")
            return True
        else:
            print("❌ Failed to create database tables")
            return False
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def test_connection():
    """Test database connection"""
    print("🧪 Testing database connection...")
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='Letmein_123',
            database='bom_comparison'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected to PostgreSQL: {version[0]}")
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print("✅ Database tables found:")
            for table in tables:
                print(f"   - {table[0]}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    print("🐳 Docker PostgreSQL Setup for BOM Comparison Tool")
    print("=" * 50)
    
    if not check_docker():
        print("❌ Docker is not running!")
        print("Please start Docker Desktop and try again")
        return False
    
    print("✅ Docker is running!")
    
    # Pull image
    if not pull_image_with_auth():
        print("\n❌ Failed to pull PostgreSQL image")
        print("This might be due to Docker Hub authentication")
        print("You can try:")
        print("1. Log in to Docker Hub: docker login")
        print("2. Or use your local PostgreSQL installation")
        return False
    
    # Start container
    if not start_container():
        print("\n❌ Failed to start PostgreSQL container")
        return False
    
    # Wait for PostgreSQL
    if not wait_for_postgres():
        print("\n❌ PostgreSQL container is not responding")
        return False
    
    # Set up tables
    if not setup_database_tables():
        print("\n❌ Failed to set up database tables")
        return False
    
    # Test connection
    if not test_connection():
        print("\n❌ Database connection test failed")
        return False
    
    print("\n🎉 Docker PostgreSQL setup completed successfully!")
    print("\n📋 Database Information:")
    print("   Host: localhost")
    print("   Port: 5432")
    print("   Database: bom_comparison")
    print("   Username: postgres")
    print("   Password: Letmein_123")
    
    print("\n🔧 Useful Docker Commands:")
    print("   Stop database: docker-compose down")
    print("   Start database: docker-compose up -d")
    print("   View logs: docker-compose logs postgres")
    print("   Remove database: docker-compose down -v")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ You can now run QA testing with Docker PostgreSQL!")
    else:
        print("\n❌ Setup failed!")
    
    input("\nPress Enter to continue...") 