#!/bin/bash
# Quick script to start the backend server

cd backend
source venv/bin/activate
PORT=${PORT:-8080}
uvicorn app:app --host 0.0.0.0 --port $PORT --reload
