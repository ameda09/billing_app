#!/usr/bin/env python3
"""
Local Network Deployment Script
Allows access from any device on the same WiFi network
"""

import subprocess
import socket
import threading
import time
import os

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "localhost"

def run_flask():
    """Run Flask backend on all interfaces"""
    print("🚀 Starting Flask backend...")
    os.system("python app.py --host=0.0.0.0 --port=5001")

def run_streamlit():
    """Run Streamlit frontend on all interfaces"""
    print("🚀 Starting Streamlit frontend...")
    time.sleep(3)  # Wait for Flask to start
    os.system("streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=8501")

if __name__ == "__main__":
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("🏪 GANPATI ELECTRONICS BILLING SYSTEM")
    print("=" * 60)
    print(f"📍 Local IP Address: {local_ip}")
    print(f"🌐 Access from any device on WiFi:")
    print(f"   📱 Main App: http://{local_ip}:8501")
    print(f"   🔧 API: http://{local_ip}:5001")
    print("=" * 60)
    print("📋 INSTRUCTIONS:")
    print("1. Share the Main App link with shop owner")
    print("2. Both devices must be on same WiFi")
    print("3. Keep this computer running")
    print("4. Press Ctrl+C to stop")
    print("=" * 60)
    
    # Start Flask in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Start Streamlit (main thread)
    run_streamlit()
