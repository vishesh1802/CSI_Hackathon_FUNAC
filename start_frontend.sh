#!/bin/bash
# Start Streamlit Frontend

cd "$(dirname "$0")/frontend"
echo "Starting Streamlit frontend..."
echo "UI will be available at http://localhost:8501"
echo ""
streamlit run app.py

