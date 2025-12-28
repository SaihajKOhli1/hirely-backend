# 🚀 Quick Start Guide - Run Everything Right Now

## Step 1: Start the Backend (Already Running!)

The backend server is already running! You can verify it by:

**Option A: Check in browser:**
- Open: http://localhost:8000/health
- You should see: `{"status": "ok", "collections": []}`

**Option B: Check in terminal:**
```bash
curl http://localhost:8000/health
```

**If it's NOT running, start it:**
```bash
cd backend
source venv/bin/activate
uvicorn app:app --reload
```

---

## Step 2: Start the Frontend

Open a **NEW terminal window** (keep the backend running in the first terminal):

```bash
# Navigate to project root
cd /Users/ahmad_afzal/Downloads/hirely-main

# Start frontend server
python3 -m http.server 3000
```

**Or use the quick script:**
```bash
./start_frontend.sh
```

---

## Step 3: Open in Browser

Once both servers are running:

1. **Frontend (Website):**
   - Open: **http://localhost:3000**
   - You'll see the Hirely landing page

2. **Backend API Docs:**
   - Open: **http://localhost:8000/docs**
   - Interactive API documentation

3. **Health Check:**
   - Open: **http://localhost:8000/health**
   - Should show: `{"status": "ok", "collections": []}`

---

## Quick Commands Summary

### Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate
uvicorn app:app --reload
```

### Terminal 2 - Frontend:
```bash
cd /Users/ahmad_afzal/Downloads/hirely-main
python3 -m http.server 3000
```

---

## What's Running?

✅ **Backend API** - http://localhost:8000
- FastAPI server
- MongoDB connected
- Health endpoint working

✅ **Frontend** - http://localhost:3000
- HTML/CSS/JavaScript website
- Landing pages
- File upload interface

---

## Testing Checklist

- [ ] Backend running: http://localhost:8000/health
- [ ] Frontend running: http://localhost:3000
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] No errors in terminal

---

## Troubleshooting

**Backend not running?**
```bash
cd backend
source venv/bin/activate
uvicorn app:app --reload
```

**Port 8000 already in use?**
```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Then restart
uvicorn app:app --reload
```

**Port 3000 already in use?**
```bash
# Use a different port
python3 -m http.server 3001
```

**Frontend not loading?**
- Make sure you're using the HTTP server (not just opening files directly)
- Check browser console for errors (F12)

---

## Next: Export to GitHub

Once everything is running, see `GITHUB_SETUP.md` for exporting to GitHub!

