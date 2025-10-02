# Dynamic Billing System - Easy Commands
# Add these to your ~/.zshrc or ~/.bashrc file

# Navigate to billing app directory
alias billing-cd='cd /Users/amedaram/Downloads/billing_app'

# Start the billing system
alias billing-start='cd /Users/amedaram/Downloads/billing_app && ./start.sh'

# Start with Python launcher (advanced)
alias billing-launch='cd /Users/amedaram/Downloads/billing_app && python3 start_app.py'

# Start with GUI launcher
alias billing-gui='cd /Users/amedaram/Downloads/billing_app && python3 launcher.py'

# Quick open in browser
alias billing-open='open http://localhost:8501'

# Stop billing system
alias billing-stop='pkill -f "python.*app.py" && pkill -f streamlit && echo "✅ Billing system stopped"'

# Check if billing system is running
alias billing-status='echo "Flask (port 5001):" && (curl -s http://localhost:5001 > /dev/null && echo "✅ Running" || echo "❌ Not running") && echo "Streamlit (port 8501):" && (curl -s http://localhost:8501 > /dev/null && echo "✅ Running" || echo "❌ Not running")'

echo "Dynamic Billing System aliases loaded!"
echo "Available commands:"
echo "  billing-start  - Start the system"
echo "  billing-stop   - Stop the system" 
echo "  billing-status - Check system status"
echo "  billing-open   - Open app in browser"
echo "  billing-gui    - Start with GUI launcher"
