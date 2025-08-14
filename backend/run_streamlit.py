#!/usr/bin/env python3
"""
Simple script to run just the Streamlit app
"""
import subprocess
import sys
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_backend():
    """Check if the FastAPI backend is running"""
    try:
        response = requests.get("http://localhost:5050/health", timeout=2)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🎨 Starting Streamlit app...")
    print("🌐 App will be available at: http://localhost:8501")
    
    # Check if backend is running
    if not check_backend():
        print("\n⚠️  WARNING: FastAPI backend is not running on localhost:5050")
        print("💡 To start the backend, run in another terminal:")
        print("   python main.py")
        print("   or")
        print("   python app.py")
        print("\n🚀 Starting Streamlit anyway...")
    else:
        print("✅ FastAPI backend is running")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "src/ui/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")