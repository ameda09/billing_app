"""
Integrated Billing System - Single Process Version
This version runs Flask inside Streamlit as a background thread
"""

import streamlit as st
import threading
import time
import subprocess
import os
import signal
import requests
from pathlib import Path

# Import your existing Flask app
import sys
sys.path.append('.')

class FlaskManager:
    def __init__(self):
        self.flask_process = None
        self.is_running = False
        
    def start_flask(self):
        """Start Flask in a separate process"""
        if self.is_running:
            return True
            
        try:
            # Start Flask process
            self.flask_process = subprocess.Popen(
                [os.path.join('my_env', 'bin', 'python'), 'app.py'],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for Flask to start
            for _ in range(10):
                try:
                    response = requests.get("http://localhost:5001/", timeout=1)
                    if response.status_code == 200:
                        self.is_running = True
                        return True
                except:
                    time.sleep(1)
                    
            return False
            
        except Exception as e:
            st.error(f"Failed to start Flask: {e}")
            return False
    
    def stop_flask(self):
        """Stop Flask process"""
        if self.flask_process:
            self.flask_process.terminate()
            self.flask_process.wait()
            self.is_running = False
    
    def check_health(self):
        """Check if Flask is healthy"""
        try:
            response = requests.get("http://localhost:5001/", timeout=2)
            return response.status_code == 200
        except:
            return False

# Initialize Flask manager
if 'flask_manager' not in st.session_state:
    st.session_state.flask_manager = FlaskManager()

# Auto-start Flask
# if not st.session_state.flask_manager.is_running:
#     with st.spinner("🚀 Starting Flask backend..."):
#         if st.session_state.flask_manager.start_flask():
#             st.success("✅ Flask backend started successfully!")
#         else:
#             st.error("❌ Failed to start Flask backend")

# Your existing Streamlit app code goes here...
# (The rest of your streamlit_app.py content)
