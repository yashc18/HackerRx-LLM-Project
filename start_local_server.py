#!/usr/bin/env python3
"""
Quick Start Script for HackRx Local Server
This script helps you start the HackRx server locally with proper setup checks.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Error: Python 3.9 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_requirements():
    """Check if requirements.txt exists"""
    if not Path("requirements.txt").exists():
        print("❌ Error: requirements.txt not found")
        print("Please ensure you're in the correct directory")
        return False
    print("✅ requirements.txt found")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("Try running: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Warning: .env file not found")
        print("Creating .env file with placeholder values...")
        
        env_content = """# HackRx Environment Variables
# Replace these with your actual API keys

# Google API Key for Gemini LLM
GOOGLE_API_KEY=your_google_api_key_here

# Hugging Face API Key (optional, for additional models)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
"""
        
        with open(env_file, "w") as f:
            f.write(env_content)
        
        print("✅ Created .env file with placeholder values")
        print("⚠️  Please update .env file with your actual API keys before testing")
        return False
    
    print("✅ .env file found")
    return True

def check_port_availability():
    """Check if port 8000 is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 8000))
        print("✅ Port 8000 is available")
        return True
    except OSError:
        print("❌ Error: Port 8000 is already in use")
        print("Please stop any existing server or change the port")
        return False

def start_server():
    """Start the HackRx server"""
    print("\n🚀 Starting HackRx Server...")
    print("=" * 50)
    
    try:
        # Start the server
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main function to run all checks and start server"""
    print("🎯 HackRx Local Server Setup")
    print("=" * 30)
    
    # Run all checks
    checks = [
        check_python_version(),
        check_requirements(),
        check_env_file(),
        check_port_availability()
    ]
    
    if not all(checks):
        print("\n❌ Setup checks failed. Please fix the issues above.")
        return
    
    # Ask if user wants to install dependencies
    if input("\n📦 Install/update dependencies? (y/n): ").lower() == 'y':
        if not install_dependencies():
            return
    
    print("\n✅ All checks passed!")
    print("\n📋 Next Steps:")
    print("1. Update .env file with your API keys")
    print("2. Open Postman and import the collection from LOCAL_POSTMAN_TESTING_GUIDE.md")
    print("3. Test the endpoints")
    print("\n🌐 Server will be available at:")
    print("   - Main API: http://localhost:8000")
    print("   - Health Check: http://localhost:8000/api/v1/health")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Main Endpoint: http://localhost:8000/hackrx/run")
    
    if input("\n🚀 Start server now? (y/n): ").lower() == 'y':
        start_server()
    else:
        print("\n💡 To start the server manually, run:")
        print("   python main.py")

if __name__ == "__main__":
    main() 