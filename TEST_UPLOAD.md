# How to Test Resume Upload

## Quick Test via Browser

1. **Open API Documentation:**
   - Go to: http://localhost:8000/docs

2. **Test Upload Endpoint:**
   - Click on `POST /upload`
   - Click "Try it out"
   - Click "Choose File" and select a PDF resume
   - Enter a company name (e.g., "Google", "Meta", "Amazon")
   - Click "Execute"
   - You should see a success response with document ID

3. **Check MongoDB:**
   - Open: http://localhost:8000/resumes
   - You'll see all uploaded resumes

## Test via Command Line

```bash
# Upload a resume
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/your/resume.pdf" \
  -F "company=Google"

# Check all resumes
curl http://localhost:8000/resumes
```

## What Gets Stored in MongoDB

Each uploaded resume is stored with:
- `company`: The company name you specified
- `filename`: Original PDF filename
- `text`: Extracted text content from PDF
- `uploaded_at`: ISO timestamp
- `_id`: Unique MongoDB document ID

