#!/bin/bash
# Start FastAPI Backend Server

cd "$(dirname "$0")/backend"
echo "Starting FastAPI backend server..."
echo "API will be available at http://localhost:8000"
echo "API docs at http://localhost:8000/docs"
echo ""
uvicorn main:app --reload --host 0.0.0.0 --port 8000

