import uvicorn
import os
import subprocess
import threading
import time
from dotenv import load_dotenv

load_dotenv()

def run_streamlit():
    """Run Streamlit app in a separate process"""
    try:
        subprocess.run([
            "streamlit", "run", "src/ui/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ])
    except Exception as e:
        print(f"Error running Streamlit: {e}")

def run_fastapi():
    """Run FastAPI app"""
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 5050)), reload=True)

if __name__ == "__main__":
    print("🚀 Starting CapitalOne Agentic Assistant...")
    print(f"📡 FastAPI will run on: http://localhost:{os.getenv('PORT', 5050)}")
    print("🎨 Streamlit will run on: http://localhost:8501")
    
    # Start Streamlit in a separate thread
    streamlit_thread = threading.Thread(target=run_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Give Streamlit a moment to start
    time.sleep(2)
    
    # Start FastAPI (this will block)
    run_fastapi()