#!/bin/bash

echo "Starting Smart Expense Tracker..."
echo ""

cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

# Check dependencies
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo ""
echo "Starting application..."
echo ""
streamlit run expense_tracker.py