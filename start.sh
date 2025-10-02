#!/bin/bash

# Dynamic Billing System Startup Script
# This script starts both Flask and Streamlit services

echo "🚀 Starting Dynamic Billing System..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to kill processes on port
kill_port() {
    local port=$1
    echo -e "${YELLOW}Killing any existing processes on port $port...${NC}"
    lsof -ti :$port | xargs kill -9 2>/dev/null || true
}

# Function to start Flask
start_flask() {
    echo -e "${BLUE}Starting Flask backend...${NC}"
    
    # Kill any existing Flask processes
    kill_port 5001
    
    # Start Flask in background
    ./my_env/bin/python app.py &
    FLASK_PID=$!
    
    # Wait for Flask to start
    for i in {1..10}; do
        if check_port 5001; then
            echo -e "${GREEN}✅ Flask backend started on port 5001${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ Failed to start Flask backend${NC}"
    return 1
}

# Function to start Streamlit
start_streamlit() {
    echo -e "${BLUE}Starting Streamlit frontend...${NC}"
    
    # Kill any existing Streamlit processes
    pkill -f streamlit 2>/dev/null || true
    sleep 1
    
    # Start Streamlit in background
    echo "" | ./my_env/bin/streamlit run streamlit_app.py &
    STREAMLIT_PID=$!
    
    # Wait for Streamlit to start
    for i in {1..15}; do
        if check_port 8501; then
            echo -e "${GREEN}✅ Streamlit frontend started on port 8501${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ Failed to start Streamlit frontend${NC}"
    return 1
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    
    # Kill Flask
    if [ ! -z "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null || true
    fi
    kill_port 5001
    
    # Kill Streamlit
    if [ ! -z "$STREAMLIT_PID" ]; then
        kill $STREAMLIT_PID 2>/dev/null || true
    fi
    pkill -f streamlit 2>/dev/null || true
    
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Setup signal handlers
trap cleanup SIGINT SIGTERM

# Start services
start_flask
if [ $? -eq 0 ]; then
    start_streamlit
    if [ $? -eq 0 ]; then
        echo "======================================"
        echo -e "${GREEN}✅ Dynamic Billing System is running!${NC}"
        echo -e "${BLUE}🌐 Flask API: http://localhost:5001${NC}"
        echo -e "${BLUE}🌐 Streamlit App: http://localhost:8501${NC}"
        echo "======================================"
        echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
        echo "======================================"
        
        # Keep script running
        while true; do
            sleep 1
        done
    else
        echo -e "${RED}❌ Failed to start Streamlit. Stopping Flask...${NC}"
        cleanup
    fi
else
    echo -e "${RED}❌ Failed to start Flask. Exiting...${NC}"
    exit 1
fi
