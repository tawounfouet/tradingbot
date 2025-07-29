#!/bin/bash

# Crypto Trading Bot Startup Script
# This script activates the virtual environment and starts the FastAPI application

echo "🚀 Starting Crypto Trading Bot..."

# Change to the project directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if requirements are installed
echo "📦 Checking dependencies..."
.venv/bin/pip list | grep -q fastapi || {
    echo "📥 Installing requirements..."
    .venv/bin/pip install -r requirements.txt
}

# Start the application
echo "🎯 Starting server..."
cd src/tradingbot
../../.venv/bin/python main.py
