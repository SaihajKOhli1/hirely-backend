# How to Run and Test Locally

This guide will help you run both the frontend and backend locally on your machine.

## Prerequisites

- Python 3.8+ installed
- MongoDB Atlas account (or local MongoDB)
- Terminal/Command Prompt

## Step-by-Step Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Make sure your .env file exists with MongoDB credentials
# If not, create it:
cat > .env << EOF
MONGO_URI=mongodb+srv://hirely:hirely123@hirely.k88noon.mongodb.net/?retryWrites=true&w=majority&appName=Hirely
DB_NAME=hirely
EOF

# Run the backend server
uvicorn app:app --reload
```

**Backend will run on:** http://localhost:8000

### 2. Frontend Setup (Open in Browser)

#### Option A: Using Python HTTP Server (Recommended)

Open a **new terminal window** (keep backend running):

```bash
# From project root directory
cd /Users/ahmad_afzal/Downloads/hirely-main

# Start a simple HTTP server
python3 -m http.server 3000
```

Then open in browser: **http://localhost:3000**

#### Option B: Open Directly

Simply double-click `index.html` or `indexdropbox.html` in Finder/File Explorer.

#### Option C: Using VS Code Live Server

If you use VS Code:
1. Install "Live Server" extension
2. Right-click on `index.html`
3. Select "Open with Live Server"

### 3. Testing the Backend

#### Test 1: Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok", "collections": []}
```

#### Test 2: API Documentation

Open in browser: **http://localhost:8000/docs**

This gives you an interactive interface to test all endpoints.

#### Test 3: Root Endpoint

```bash
curl http://localhost:8000/
```

### 4. Testing the Frontend

1. **Open the landing page:**
   - http://localhost:3000 (if using HTTP server)
   - Or open `index.html` directly

2. **Open the upload page:**
   - http://localhost:3000/indexdropbox.html
   - Or open `indexdropbox.html` directly

3. **Check if frontend connects to backend:**
   - Open browser Developer Tools (F12)
   - Go to Network tab
   - Try uploading a file (if upload functionality is implemented)
   - Check if requests are being sent to `http://localhost:8000`

## Quick Start Commands

### Start Backend:
```bash
cd backend
source venv/bin/activate  # Only if not already activated
uvicorn app:app --reload
```

### Start Frontend Server:
```bash
# In a new terminal
python3 -m http.server 3000
```

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
uvicorn app:app --reload --port 8001
```

**MongoDB connection error:**
- Check your `.env` file has correct credentials
- Verify MongoDB Atlas network access allows your IP
- Make sure SSL/TLS is enabled

**Import errors:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Issues

**CORS errors when connecting to backend:**
- The backend needs CORS middleware (we can add this if needed)
- Or use a proxy

**Files not loading:**
- Make sure you're using a web server (not just opening files directly)
- Check browser console for errors

## Testing Checklist

- [ ] Backend server starts without errors
- [ ] Health endpoint returns `{"status": "ok"}`
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Frontend loads in browser
- [ ] No console errors in browser
- [ ] MongoDB connection working (check /health endpoint)

## Next Steps

Once everything is running:

1. **Test API endpoints** using the Swagger UI at http://localhost:8000/docs
2. **Connect frontend to backend** (if not already connected)
3. **Test file uploads** (if upload endpoint is implemented)
4. **Check MongoDB** to see if data is being stored

## Development Workflow

1. **Backend changes:**
   - Edit `backend/app.py` or `backend/db.py`
   - Server auto-reloads (thanks to `--reload` flag)
   - Test changes immediately

2. **Frontend changes:**
   - Edit HTML files
   - Refresh browser to see changes
   - Check browser console for errors

3. **Database changes:**
   - Check MongoDB Atlas dashboard
   - Or use MongoDB Compass to view data

