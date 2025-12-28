#!/bin/bash
# Quick script to start the backend server

cd backend
source venv/bin/activate
uvicorn app:app --reload
