# How to Check MongoDB for Uploaded Resumes

## Method 1: Using the API Endpoint (Easiest)

**Check all resumes:**
```bash
curl http://localhost:8000/resumes
```

**Or open in browser:**
- http://localhost:8000/resumes

This will show you all uploaded resumes with:
- Document ID
- Company name
- Filename
- Upload timestamp

## Method 2: Using MongoDB Atlas Dashboard

1. Go to https://cloud.mongodb.com
2. Sign in to your account
3. Select your cluster
4. Click "Browse Collections"
5. Select the `hirely` database
6. Click on the `resumes` collection
7. You'll see all uploaded resumes with their data

## Method 3: Using MongoDB Compass (Desktop App)

1. Download MongoDB Compass: https://www.mongodb.com/products/compass
2. Connect using your connection string from `.env`:
   ```
   mongodb+srv://hirely:hirely123@hirely.k88noon.mongodb.net/
   ```
3. Navigate to `hirely` database → `resumes` collection
4. View all documents

## Method 4: Using Python Script

Create a quick script to check:

```bash
cd backend
source venv/bin/activate
python3 -c "
import asyncio
from db import get_db

async def check_resumes():
    db = await get_db()
    collection = db.resumes
    count = await collection.count_documents({})
    print(f'Total resumes: {count}')
    cursor = collection.find({})
    async for doc in cursor:
        print(f\"ID: {doc['_id']}, Company: {doc.get('company', 'N/A')}, File: {doc.get('filename', 'N/A')}\")

asyncio.run(check_resumes())
"
```

## Quick Test

After uploading a resume, immediately check:

```bash
# Check if resumes collection exists and has data
curl http://localhost:8000/health

# List all resumes
curl http://localhost:8000/resumes
```

## What to Look For

When you check MongoDB, you should see documents like:

```json
{
  "_id": "507f1f77bcf86cd799439011",
  "company": "Google",
  "filename": "resume.pdf",
  "text": "Extracted text from PDF...",
  "uploaded_at": "2025-11-05T21:48:30.123456"
}
```

