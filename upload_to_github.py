#!/usr/bin/env python3
"""
Script to help upload the BOM Comparison Tool to GitHub
"""

import os
import subprocess
import sys

def check_git():
    """Check if git is installed"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Git not found")
            return False
    except FileNotFoundError:
        print("❌ Git not installed")
        return False

def init_git_repo():
    """Initialize git repository"""
    print("🔧 Initializing Git repository...")
    
    try:
        # Check if already a git repo
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository already initialized")
            return True
        
        # Initialize new repo
        result = subprocess.run(['git', 'init'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository initialized")
            return True
        else:
            print(f"❌ Failed to initialize git: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error initializing git: {e}")
        return False

def add_files():
    """Add all files to git"""
    print("📁 Adding files to git...")
    
    try:
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Files added to git")
            return True
        else:
            print(f"❌ Failed to add files: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error adding files: {e}")
        return False

def commit_files():
    """Commit files with initial message"""
    print("💾 Committing files...")
    
    try:
        result = subprocess.run(['git', 'commit', '-m', 'Initial commit: BOM Comparison Tool'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Files committed")
            return True
        else:
            print(f"❌ Failed to commit: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error committing: {e}")
        return False

def create_github_repo():
    """Instructions for creating GitHub repository"""
    print("\n🌐 GitHub Repository Setup")
    print("=" * 40)
    print("1. Go to https://github.com/new")
    print("2. Repository name: bom-comparison-tool")
    print("3. Description: A powerful web-based tool for comparing Bill of Materials (BOM) Excel files")
    print("4. Make it Public or Private (your choice)")
    print("5. DO NOT initialize with README (we already have one)")
    print("6. Click 'Create repository'")
    print("\nAfter creating the repository, you'll get a URL like:")
    print("https://github.com/yourusername/bom-comparison-tool.git")
    print("\nUse this URL in the next step.")

def add_remote_repo():
    """Add remote repository"""
    print("\n🔗 Adding remote repository...")
    
    # Get repository URL from user
    repo_url = input("Enter your GitHub repository URL: ").strip()
    
    if not repo_url:
        print("❌ No repository URL provided")
        return False
    
    try:
        result = subprocess.run(['git', 'remote', 'add', 'origin', repo_url], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Remote repository added")
            return True
        else:
            print(f"❌ Failed to add remote: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error adding remote: {e}")
        return False

def push_to_github():
    """Push to GitHub"""
    print("🚀 Pushing to GitHub...")
    
    try:
        result = subprocess.run(['git', 'push', '-u', 'origin', 'main'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Successfully pushed to GitHub!")
            return True
        else:
            print(f"❌ Failed to push: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error pushing: {e}")
        return False

def main():
    print("🚀 GitHub Upload Helper for BOM Comparison Tool")
    print("=" * 50)
    
    # Check git
    if not check_git():
        print("\n❌ Please install Git first:")
        print("   Download from: https://git-scm.com/downloads")
        return False
    
    # Initialize git repo
    if not init_git_repo():
        print("\n❌ Failed to initialize git repository")
        return False
    
    # Add files
    if not add_files():
        print("\n❌ Failed to add files to git")
        return False
    
    # Commit files
    if not commit_files():
        print("\n❌ Failed to commit files")
        return False
    
    # Create GitHub repo instructions
    create_github_repo()
    
    # Add remote
    if not add_remote_repo():
        print("\n❌ Failed to add remote repository")
        return False
    
    # Push to GitHub
    if not push_to_github():
        print("\n❌ Failed to push to GitHub")
        return False
    
    print("\n🎉 Success! Your project is now on GitHub!")
    print("\n📋 Next Steps:")
    print("1. Go to your GitHub repository")
    print("2. Check that all files are uploaded")
    print("3. Enable GitHub Actions (if desired)")
    print("4. Add collaborators (if needed)")
    print("5. Create issues for bugs/features")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ GitHub upload completed successfully!")
    else:
        print("\n❌ GitHub upload failed!")
    
    input("\nPress Enter to continue...") 