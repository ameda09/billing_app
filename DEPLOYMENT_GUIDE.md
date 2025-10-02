# Deployment Guide for Billing App

This billing app is ready for cloud deployment on Railway.app (free tier available).

## Quick Deploy to Railway

### Option 1: Direct Deploy (Recommended)
1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "Deploy from GitHub repo"
4. Upload this entire billing_app folder or connect your GitHub repo
5. Railway will automatically detect the Python app and deploy it
6. Your app will be available at: `https://your-app-name.railway.app`

### Option 2: Using Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

## Files Included for Deployment

- `Procfile`: Tells Railway how to start the app
- `requirements.txt`: Python dependencies
- `runtime.txt`: Python version specification
- `railway.json`: Railway configuration
- `deployment_app.py`: Combined Flask + Streamlit launcher for cloud

## Environment Variables (automatically handled)

- `PORT`: Set by Railway for the main service (Streamlit frontend)
- `FLASK_PORT`: Internal port for Flask backend (5001)
- `BACKEND_URL`: Automatically set to localhost:5001 for internal communication

## What Gets Deployed

1. **Flask Backend** (Port 5001): Handles PDF generation, bill management, API endpoints
2. **Streamlit Frontend** (Main Port): User interface for the billing system

## Access Your Deployed App

After deployment, you'll get a public URL like:
`https://billing-app-production.railway.app`

This URL can be shared with anyone to access your billing system online.

## Features Available Online

✅ Complete billing system with inventory management
✅ Professional PDF bill generation
✅ Customer and bill management
✅ Product catalog and shopping cart
✅ Bill history and deletion
✅ Mobile-responsive interface
✅ Static shop details (Ganpati Electronics and E Services)
✅ INR (₹) currency format
✅ No tax calculations (as requested)

## Data Storage

- Bills and inventory are stored in CSV files
- Data persists between app restarts
- For production use, consider upgrading to a database

## Security Note

The deployed app will be publicly accessible. Consider adding authentication if sensitive data is involved.
