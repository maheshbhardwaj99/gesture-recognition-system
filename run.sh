#!/bin/bash

echo ""
echo "=================================================="
echo "  🖐️  Gesture Recognition System — Setup & Run"
echo "=================================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

echo "📥 Installing dependencies (first time may take 1-2 min)..."
pip install -q -r requirements.txt

echo ""
echo "🚀 Starting Gesture Recognition App..."
echo ""
echo "  ➜  Open: http://localhost:5000"
echo "  ➜  Press Ctrl+C to stop"
echo ""

python3 app.py
