# Hirely Codebase Analysis

## 1. Current Architecture

### Frontend
- **Technology**: Vanilla HTML/CSS/JavaScript (no framework)
- **Files**: 
  - `index.html` - Marketing landing page
  - `indexdropbox.html` - Resume upload/analysis prototype page
  - `index.ts` - TypeScript type definitions (interfaces only, not used in runtime)

**What it does:**
- Landing page (`index.html`) displays marketing content, company logos, FAQ, and a waitlist form
- Prototype page (`indexdropbox.html`) allows users to:
  - Select a company (Google, Meta, Amazon, Microsoft, NVIDIA, or "All Companies")
  - Upload a PDF resume file
  - Paste resume text directly
  - View mock analysis results with scores, metrics, and feedback

**Note**: The frontend currently uses **mock/fake data** for analysis results. Even when uploading to the backend, it ignores the backend response and shows hardcoded analysis results.

### Backend
- **Technology**: FastAPI (Python)
- **Entry Point**: `backend/app.py` (FastAPI application)
- **Database**: MongoDB (via Motor async driver)
- **Run Command**: `uvicorn app:app --reload` (or `./start_backend.sh`)

**What it does:**
- Accepts PDF file uploads via `/upload` endpoint
- Extracts text from PDFs using PyMuPDF (fitz library)
- Stores extracted text, filename, company name, and timestamp in MongoDB
- Provides endpoints to retrieve stored resumes
- **Does NOT perform any AI analysis or resume critique** - it only stores raw text

### Connection Status
- **Partially Connected**: The frontend CAN upload files to the backend, but:
  - Frontend hardcodes API URL to `http://localhost:8000/upload`
  - After successful upload, frontend discards backend response and shows mock analysis instead
  - No real analysis endpoint exists - the `/critique` endpoint mentioned in `index.html` line 674 does not exist

---

## 2. Backend Entry Point

**File**: `backend/app.py`

**Start Command**:
```bash
cd backend
uvicorn app:app --reload
```

Or use the helper script:
```bash
./start_backend.sh
```

**FastAPI Application**: The `app` object is defined at line 12 in `app.py`:
```python
app = FastAPI(
    title="Hirely API",
    description="Backend API for Hirely",
    version="1.0.0"
)
```

---

## 3. Resume Parsing Flow (Step-by-Step)

### When a PDF is uploaded:

1. **Frontend (`indexdropbox.html` lines 827-876)**:
   - User selects a PDF file via file input
   - `handleFileSelect()` function is triggered
   - `analyzeFile()` function validates file (PDF only, max 10MB)
   - Creates FormData with file and company name
   - Sends POST request to `http://localhost:8000/upload`

2. **Backend (`backend/app.py` lines 48-121)**:
   - FastAPI receives POST request at `/upload` endpoint
   - Validates file is PDF (line 67)
   - Validates company field is not empty (line 74)
   - Reads file content into memory (line 82)
   - Calls `extract_text_from_pdf(file_content)` (line 85)

3. **Text Extraction (`backend/utils/extract_text.py`)**:
   - Uses PyMuPDF library (`fitz`) to open PDF from bytes (line 25)
   - Iterates through all pages (lines 29-33)
   - Extracts text from each page using `page.get_text()` (line 31)
   - Joins pages with double newlines (line 38)
   - Cleans whitespace but preserves structure (line 41)
   - Returns extracted text as string

4. **Storage (`backend/app.py` lines 88-100)**:
   - Connects to MongoDB using `get_db()` (line 88)
   - Accesses `resumes` collection (line 89)
   - Creates document with:
     - `company`: Company name from form
     - `filename`: Original filename
     - `text`: Extracted text
     - `uploaded_at`: ISO timestamp
   - Inserts document into MongoDB (line 100)
   - Returns JSON response with document ID and metadata

5. **Frontend Response Handling (`indexdropbox.html` lines 861-868)**:
   - Receives success response from backend
   - Shows success message with document ID
   - **THEN IGNORES BACKEND RESPONSE**
   - Calls `generateMockFileAnalysis()` (line 868) to create fake results
   - Displays mock analysis to user

**Key Issue**: The extracted text is stored in MongoDB but never used for actual analysis. The frontend always shows hardcoded mock data.

---

## 4. API Endpoints

### Existing Endpoints:

| Method | Path | Input | Output |
|--------|------|-------|--------|
| `GET` | `/health` | None | `{"status": "ok", "collections": [...]}` - MongoDB connection status |
| `POST` | `/upload` | `file` (PDF), `company` (string) | `{"success": true, "message": "...", "document_id": "...", "company": "...", "filename": "...", "uploaded_at": "..."}` |
| `GET` | `/resumes` | None | `{"success": true, "count": N, "resumes": [...]}` - List all resumes (without text field) |
| `GET` | `/resumes/{resume_id}` | `resume_id` (string) | `{"success": true, "resume": {...}}` - Full resume including text |
| `GET` | `/view` | None | `[...]` - Array of all resume documents with full data |

### Missing Endpoints:

- `/critique` - Referenced in `index.html` line 674 but does not exist
- `/analyze` - No endpoint for actual resume analysis
- Any endpoint that returns structured analysis (scores, feedback, metrics)

---

## 5. Missing or Broken Components

### Critical Missing Features:

1. **No AI/Analysis Endpoint**
   - The `/critique` endpoint mentioned in `index.html` does not exist
   - Backend only stores text, never analyzes it
   - Frontend uses 100% mock data for all analysis results

2. **Frontend Disconnected from Backend Analysis**
   - `indexdropbox.html` line 868: After upload, immediately returns `generateMockFileAnalysis()`
   - Backend response is acknowledged but ignored for analysis
   - Text paste functionality (`analyzeText()`) has no backend at all - 100% mock

3. **Hardcoded API URL**
   - `indexdropbox.html` line 851: `fetch('http://localhost:8000/upload')`
   - Will not work in production/deployment
   - Not configurable via environment variables

4. **CORS Limitations**
   - `backend/app.py` lines 21: Only allows `http://localhost:3000` and `http://127.0.0.1:3000`
   - Will fail if frontend runs on different port or domain

5. **Unused Files**
   - `index.ts` - TypeScript definitions exported but never imported/used (no TypeScript compilation)
   - Likely leftover from planning phase

6. **No Environment Configuration for Frontend**
   - No way to set API URL without editing code
   - No build process or configuration system

7. **Text Analysis Not Implemented**
   - `analyzeText()` function in frontend (line 879) has no backend call
   - Just returns mock data after delay

8. **File Type Validation Mismatch**
   - Frontend accepts `.pdf, .doc, .docx` (line 549)
   - Backend only accepts `.pdf` (line 67)
   - DOC/DOCX uploads will fail on backend

9. **No Error Handling for MongoDB Connection Failures**
   - If MongoDB is down, `/upload` will fail with generic 500 error
   - `get_db()` doesn't handle connection errors gracefully

10. **No Authentication/Authorization**
    - All endpoints are publicly accessible
    - No rate limiting
    - No user accounts or session management

### Code Issues:

1. **Unused Import** (`backend/app.py` line 5):
   - `Annotated` is imported but never used

2. **Inconsistent Error Handling**:
   - Some endpoints catch specific exceptions, others catch all
   - Error messages vary in format

3. **No Input Sanitization**:
   - Company name is stored directly without validation (could be empty string after strip)
   - No validation on filename format

---

## 6. Frontend-Backend Communication

### Current Configuration:

**API URL Location**: `indexdropbox.html` line 851
```javascript
const response = await fetch('http://localhost:8000/upload', {
    method: 'POST',
    body: formData
});
```

**Hardcoded**: Yes, directly in JavaScript code

**Local vs Deployed**:
- **Local**: Will work IF:
  - Backend runs on `localhost:8000`
  - Frontend runs on `localhost:3000` (or CORS is updated)
  - MongoDB connection is configured
  
- **Deployed**: Will NOT work because:
  - Hardcoded `localhost:8000` won't resolve to production server
  - CORS only allows localhost origins
  - No environment variable system to configure API URL

**Communication Flow**:
1. Frontend sends FormData with file + company to `/upload`
2. Backend validates, extracts text, stores in MongoDB
3. Backend returns success with document ID
4. Frontend shows success message but ignores actual data
5. Frontend generates and displays mock analysis results

**Missing Communication**:
- Frontend never requests analysis from backend
- Frontend never retrieves stored resumes for display
- Text paste feature has zero backend integration

---

## 7. Summary (10 Bullet Points)

### What Works:

✅ **Backend file upload and storage**: PDF uploads work, text extraction works, MongoDB storage works  
✅ **PDF text extraction**: PyMuPDF successfully extracts text from PDF files  
✅ **Frontend UI**: Beautiful, functional interface with animations and responsive design  
✅ **Basic API endpoints**: Health check, upload, and resume retrieval endpoints function correctly  
✅ **CORS setup**: Configured for local development (though limited to localhost:3000)  

### What Doesn't Work:

❌ **Resume analysis**: No AI/analysis functionality exists - all results are hardcoded mock data  
❌ **Text paste feature**: Completely disconnected from backend, returns fake data  
❌ **Production deployment**: Hardcoded localhost URLs prevent deployment  
❌ **DOC/DOCX support**: Frontend accepts them but backend rejects them  
❌ **Environment configuration**: No way to configure API URLs without code changes  

### What Must Be Fixed Before Deployment:

🔧 **Implement actual analysis endpoint** (`/critique` or `/analyze`) that processes stored text and returns real scores/feedback  
🔧 **Replace mock data in frontend** with actual API calls to analysis endpoint  
🔧 **Make API URL configurable** (environment variables or config file)  
🔧 **Update CORS settings** to allow production frontend domain  
🔧 **Add error handling** for MongoDB connection failures and network issues  
🔧 **Fix file type handling** - either remove DOC/DOCX from frontend or add support in backend  
🔧 **Remove unused code** (`Annotated` import, unused `index.ts` if not needed)  

---

## Additional Notes

- The codebase appears to be in a **proof-of-concept stage** where the infrastructure (upload, storage) is built but the core feature (resume analysis) is not implemented
- The frontend is production-ready in terms of UI/UX but functionally incomplete
- The backend is functional for storage but missing the analysis layer that would make it useful
- MongoDB connection requires `.env` file with `MONGO_URI` and `DB_NAME` (not included in repo, as expected)

