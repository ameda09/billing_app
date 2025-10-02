#!/usr/bin/env python3
"""
One-Click Billing System Launcher
Double-click this file to start the entire billing system
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import threading
import os
import sys
import time
import requests
from pathlib import Path

class BillingSystemLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dynamic Billing System Launcher")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set working directory
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        self.flask_process = None
        self.streamlit_process = None
        self.is_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="🧾 Dynamic Billing System", 
            font=("Arial", 20, "bold"),
            fg="#1e40af"
        )
        title_label.pack(pady=20)
        
        # Status frame
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="Status: Not Running",
            font=("Arial", 12),
            fg="red"
        )
        self.status_label.pack()
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.start_btn = tk.Button(
            button_frame,
            text="🚀 Start System",
            command=self.start_system,
            font=("Arial", 14, "bold"),
            bg="#10b981",
            fg="white",
            padx=20,
            pady=10
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="🛑 Stop System",
            command=self.stop_system,
            font=("Arial", 14, "bold"),
            bg="#ef4444",
            fg="white",
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        self.open_btn = tk.Button(
            button_frame,
            text="🌐 Open App",
            command=self.open_app,
            font=("Arial", 14, "bold"),
            bg="#3b82f6",
            fg="white",
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.open_btn.pack(side=tk.LEFT, padx=10)
        
        # Log area
        log_label = tk.Label(self.root, text="System Logs:", font=("Arial", 12, "bold"))
        log_label.pack(pady=(20, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            self.root,
            height=15,
            width=70,
            font=("Consolas", 10)
        )
        self.log_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Auto-refresh status
        self.check_status()
        
    def log(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def check_status(self):
        """Check system status"""
        flask_ok = self.check_flask()
        streamlit_ok = self.check_streamlit()
        
        if flask_ok and streamlit_ok:
            self.status_label.config(text="Status: ✅ Running", fg="green")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.open_btn.config(state=tk.NORMAL)
            self.is_running = True
        elif flask_ok or streamlit_ok:
            self.status_label.config(text="Status: ⚠️ Partially Running", fg="orange")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.open_btn.config(state=tk.DISABLED)
            self.is_running = False
        else:
            self.status_label.config(text="Status: ❌ Not Running", fg="red")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.open_btn.config(state=tk.DISABLED)
            self.is_running = False
            
        # Schedule next check
        self.root.after(3000, self.check_status)
        
    def check_flask(self):
        """Check if Flask is running"""
        try:
            response = requests.get("http://localhost:5001/", timeout=2)
            return response.status_code == 200
        except:
            return False
            
    def check_streamlit(self):
        """Check if Streamlit is running"""
        try:
            response = requests.get("http://localhost:8501/", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start_system(self):
        """Start the billing system"""
        def start_thread():
            try:
                self.log("🚀 Starting Dynamic Billing System...")
                
                # Start Flask
                self.log("Starting Flask backend...")
                self.flask_process = subprocess.Popen(
                    [os.path.join('my_env', 'bin', 'python'), 'app.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Wait for Flask
                for i in range(10):
                    if self.check_flask():
                        self.log("✅ Flask backend started on port 5001")
                        break
                    time.sleep(1)
                else:
                    self.log("❌ Flask failed to start")
                    return
                
                # Start Streamlit
                self.log("Starting Streamlit frontend...")
                # Kill existing Streamlit
                subprocess.run(['pkill', '-f', 'streamlit'], capture_output=True)
                time.sleep(1)
                
                self.streamlit_process = subprocess.Popen(
                    [os.path.join('my_env', 'bin', 'streamlit'), 'run', 'streamlit_app.py', '--server.headless', 'true'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Wait for Streamlit
                for i in range(15):
                    if self.check_streamlit():
                        self.log("✅ Streamlit frontend started on port 8501")
                        break
                    time.sleep(1)
                else:
                    self.log("❌ Streamlit failed to start")
                    return
                
                self.log("🎉 System started successfully!")
                self.log("🌐 Flask API: http://localhost:5001")
                self.log("🌐 Streamlit App: http://localhost:8501")
                
            except Exception as e:
                self.log(f"❌ Error starting system: {e}")
        
        threading.Thread(target=start_thread, daemon=True).start()
    
    def stop_system(self):
        """Stop the billing system"""
        self.log("🛑 Stopping system...")
        
        if self.flask_process:
            self.flask_process.terminate()
            self.flask_process = None
            
        if self.streamlit_process:
            self.streamlit_process.terminate()
            self.streamlit_process = None
            
        # Kill any remaining processes
        subprocess.run(['pkill', '-f', 'streamlit'], capture_output=True)
        subprocess.run(['pkill', '-f', 'app.py'], capture_output=True)
        
        self.log("✅ System stopped")
    
    def open_app(self):
        """Open the app in browser"""
        import webbrowser
        webbrowser.open("http://localhost:8501")
        self.log("🌐 Opening app in browser...")
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_running:
            if messagebox.askokcancel("Quit", "Stop the billing system and quit?"):
                self.stop_system()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Run the launcher"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    launcher = BillingSystemLauncher()
    launcher.run()
