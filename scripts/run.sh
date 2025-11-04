#!/bin/bash

echo "Starting Impact Analysis Tool..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependenciess..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please update .env with your GEMINI_API_KEY"
fi

# Run the server
echo "Starting server on http://localhost:8000"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
