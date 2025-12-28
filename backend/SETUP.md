# How to Run the Backend

## Prerequisites
- Python 3.8 or higher
- MongoDB installed and running (or MongoDB Atlas connection string)

## Step 1: Navigate to the backend directory
```bash
cd backend
```

## Step 2: Create and activate a virtual environment (recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

## Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

## Step 4: Create .env file
Create a `.env` file in the `backend/` directory with your MongoDB connection details:

```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=hirely
```

**For MongoDB Atlas (cloud):**
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=hirely
```

**For local MongoDB with authentication:**
```env
MONGO_URI=mongodb://username:password@localhost:27017/
DB_NAME=hirely
```

## Step 5: Start MongoDB (if running locally)
Make sure MongoDB is running on your system:
```bash
# macOS (if installed via Homebrew):
brew services start mongodb-community

# Linux:
sudo systemctl start mongod

# Or check if it's running:
mongosh --eval "db.adminCommand('ping')"
```

## Step 6: Run the FastAPI server
```bash
uvicorn app:app --reload
```

The server will start at: **http://localhost:8000**

## Step 7: Test the API
- API Documentation: http://localhost:8000/docs (Interactive Swagger UI)
- Alternative API Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health
- Root Endpoint: http://localhost:8000/

## Testing the Upload Endpoint

You can test the `/upload` endpoint using curl:

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/your/resume.pdf" \
  -F "company=Google"
```

Or using the interactive docs at http://localhost:8000/docs - just click on `/upload`, click "Try it out", upload a PDF file, enter a company name, and click "Execute".

