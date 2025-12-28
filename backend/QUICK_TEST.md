# Quick Test - Verify Upload Works

## After Server Reset

The server has been reset. MongoDB is empty because no successful uploads have happened yet.

## Test Upload Now

1. **Open API Docs:**
   - http://localhost:8000/docs

2. **Test Upload:**
   - Click `POST /upload`
   - Click "Try it out"
   - In "file" field, click "Choose File" and select a PDF
   - In "company" field, enter: `Google` (or any company name)
   - Click "Execute"

3. **Check Result:**
   - You should see a success response with document ID
   - Then check: http://localhost:8000/view
   - You should see your uploaded document!

## If Upload Fails

- Make sure file is a PDF (`.pdf` extension)
- Check server terminal for error messages
- Verify MongoDB connection in `.env` file

## View All Data

- **All data:** http://localhost:8000/view
- **Resumes list:** http://localhost:8000/resumes
- **Health check:** http://localhost:8000/health

