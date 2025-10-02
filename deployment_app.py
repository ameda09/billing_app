# deployment_app.py - Combined Flask + Streamlit for cloud deployment
import subprocess
import threading
import time
import os
import sys
from app import app  # Import your Flask app

def run_flask():
    """Run Flask backend"""
    flask_port = int(os.environ.get("FLASK_PORT", 5001))
    print(f"Starting Flask on port {flask_port}")
    app.run(host='0.0.0.0', port=flask_port, debug=False, threaded=True)

def run_streamlit():
    """Run Streamlit frontend"""
    # Wait a bit for Flask to start
    time.sleep(5)
    streamlit_port = int(os.environ.get("PORT", 8501))  # Railway uses PORT for main service
    print(f"Starting Streamlit on port {streamlit_port}")
    
    # Set backend URL for Streamlit
    os.environ["BACKEND_URL"] = f"http://localhost:5001"
    
    try:
        subprocess.run([
            "streamlit", "run", "streamlit_app.py", 
            "--server.port", str(streamlit_port),
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableXsrfProtection", "false",
            "--server.enableCORS", "false"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Streamlit failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting deployment...")
    print(f"Environment: PORT={os.environ.get('PORT', 'not set')}")
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start Streamlit in main thread
    run_streamlit()
