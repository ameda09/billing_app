#!/usr/bin/env python3
"""
Master startup script for the Dynamic Billing System
This script ensures both Flask backend and Streamlit frontend are always running
"""

import subprocess
import time
import os
import signal
import sys
import threading
import requests
from pathlib import Path

# Configuration
FLASK_PORT = 5001
STREAMLIT_PORT = 8501
CHECK_INTERVAL = 5  # seconds
MAX_RESTART_ATTEMPTS = 3

class BillingSystemManager:
    def __init__(self):
        self.flask_process = None
        self.streamlit_process = None
        self.running = True
        self.flask_restart_count = 0
        self.streamlit_restart_count = 0
        
    def is_port_in_use(self, port):
        """Check if a port is in use"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0
        except:
            return False
    
    def check_flask_health(self):
        """Check if Flask API is responding"""
        try:
            response = requests.get(f"http://localhost:{FLASK_PORT}/", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def check_streamlit_health(self):
        """Check if Streamlit is responding"""
        try:
            response = requests.get(f"http://localhost:{STREAMLIT_PORT}/", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def start_flask(self):
        """Start Flask backend"""
        print("🚀 Starting Flask backend...")
        try:
            env = os.environ.copy()
            env['FLASK_ENV'] = 'development'
            
            self.flask_process = subprocess.Popen(
                [os.path.join('my_env', 'bin', 'python'), 'app.py'],
                cwd=os.getcwd(),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            # Wait a moment for Flask to start
            time.sleep(3)
            
            if self.check_flask_health():
                print(f"✅ Flask backend started successfully on port {FLASK_PORT}")
                self.flask_restart_count = 0
                return True
            else:
                print("❌ Flask backend failed to start properly")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Flask: {e}")
            return False
    
    def start_streamlit(self):
        """Start Streamlit frontend"""
        print("🚀 Starting Streamlit frontend...")
        try:
            # Kill any existing Streamlit processes
            subprocess.run(['pkill', '-f', 'streamlit'], capture_output=True)
            time.sleep(1)
            
            self.streamlit_process = subprocess.Popen(
                [os.path.join('my_env', 'bin', 'streamlit'), 'run', 'streamlit_app.py', 
                 '--server.port', str(STREAMLIT_PORT), '--server.headless', 'true'],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            # Wait for Streamlit to start
            for i in range(15):  # Wait up to 15 seconds
                if self.is_port_in_use(STREAMLIT_PORT):
                    print(f"✅ Streamlit frontend started successfully on port {STREAMLIT_PORT}")
                    self.streamlit_restart_count = 0
                    return True
                time.sleep(1)
            
            print("❌ Streamlit frontend failed to start properly")
            return False
            
        except Exception as e:
            print(f"❌ Error starting Streamlit: {e}")
            return False
    
    def restart_flask(self):
        """Restart Flask backend"""
        if self.flask_restart_count >= MAX_RESTART_ATTEMPTS:
            print(f"❌ Flask has been restarted {MAX_RESTART_ATTEMPTS} times. Manual intervention required.")
            return False
            
        print("🔄 Restarting Flask backend...")
        self.stop_flask()
        time.sleep(2)
        self.flask_restart_count += 1
        return self.start_flask()
    
    def restart_streamlit(self):
        """Restart Streamlit frontend"""
        if self.streamlit_restart_count >= MAX_RESTART_ATTEMPTS:
            print(f"❌ Streamlit has been restarted {MAX_RESTART_ATTEMPTS} times. Manual intervention required.")
            return False
            
        print("🔄 Restarting Streamlit frontend...")
        self.stop_streamlit()
        time.sleep(2)
        self.streamlit_restart_count += 1
        return self.start_streamlit()
    
    def stop_flask(self):
        """Stop Flask backend"""
        if self.flask_process:
            try:
                os.killpg(os.getpgid(self.flask_process.pid), signal.SIGTERM)
                self.flask_process.wait(timeout=5)
            except:
                try:
                    os.killpg(os.getpgid(self.flask_process.pid), signal.SIGKILL)
                except:
                    pass
            self.flask_process = None
    
    def stop_streamlit(self):
        """Stop Streamlit frontend"""
        if self.streamlit_process:
            try:
                os.killpg(os.getpgid(self.streamlit_process.pid), signal.SIGTERM)
                self.streamlit_process.wait(timeout=5)
            except:
                try:
                    os.killpg(os.getpgid(self.streamlit_process.pid), signal.SIGKILL)
                except:
                    pass
            self.streamlit_process = None
        
        # Also kill any remaining Streamlit processes
        subprocess.run(['pkill', '-f', 'streamlit'], capture_output=True)
    
    def monitor_services(self):
        """Monitor both services and restart if needed"""
        print("👀 Starting service monitoring...")
        
        while self.running:
            try:
                # Check Flask
                if not self.check_flask_health():
                    print("⚠️ Flask backend is not responding. Attempting restart...")
                    if not self.restart_flask():
                        print("💥 Failed to restart Flask backend!")
                
                # Check Streamlit
                if not self.is_port_in_use(STREAMLIT_PORT):
                    print("⚠️ Streamlit frontend is not responding. Attempting restart...")
                    if not self.restart_streamlit():
                        print("💥 Failed to restart Streamlit frontend!")
                
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(CHECK_INTERVAL)
    
    def start_all(self):
        """Start both services"""
        print("🚀 Starting Dynamic Billing System...")
        print("=" * 50)
        
        # Start Flask first
        if not self.start_flask():
            print("❌ Failed to start Flask backend. Exiting...")
            return False
        
        # Start Streamlit
        if not self.start_streamlit():
            print("❌ Failed to start Streamlit frontend. Exiting...")
            self.stop_flask()
            return False
        
        print("=" * 50)
        print("✅ Both services started successfully!")
        print(f"🌐 Flask API: http://localhost:{FLASK_PORT}")
        print(f"🌐 Streamlit App: http://localhost:{STREAMLIT_PORT}")
        print("=" * 50)
        print("📊 Service monitoring active...")
        print("Press Ctrl+C to stop all services")
        print("=" * 50)
        
        return True
    
    def stop_all(self):
        """Stop all services"""
        print("\n🛑 Stopping all services...")
        self.running = False
        self.stop_flask()
        self.stop_streamlit()
        print("✅ All services stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n📡 Received signal {signum}")
        self.stop_all()
        sys.exit(0)

def main():
    """Main function"""
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    manager = BillingSystemManager()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    try:
        # Start all services
        if manager.start_all():
            # Start monitoring in a separate thread
            monitor_thread = threading.Thread(target=manager.monitor_services)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Keep main thread alive
            while manager.running:
                time.sleep(1)
        
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop_all()

if __name__ == "__main__":
    main()
