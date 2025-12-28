"""
FastAPI backend application.
"""
from datetime import datetime
from typing import Annotated
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from db import get_db
from utils.extract_text import extract_text_from_pdf

app = FastAPI(
    title="Hirely API",
    description="Backend API for Hirely",
    version="1.0.0"
)

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint that verifies MongoDB connection and returns collections.
    """
    try:
        db = await get_db()
        # List all collection names
        collections = await db.list_collection_names()
        return {
            "status": "ok",
            "collections": collections
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@app.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    company: str = Form(...)
):
    """
    Upload a PDF resume and store extracted text in MongoDB.
    
    Args:
        file: PDF file to upload
        company: Name of the company the resume is for
        
    Returns:
        JSONResponse: Confirmation response with upload details
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are accepted. Please upload a PDF file."
        )
    
    # Validate company field
    if not company or not company.strip():
        raise HTTPException(
            status_code=400,
            detail="Company name is required and cannot be empty"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract text from PDF (excluding metadata)
        extracted_text = extract_text_from_pdf(file_content)
        
        # Get database and collection
        db = await get_db()
        resumes_collection = db.resumes
        
        # Prepare document
        resume_document = {
            "company": company.strip(),
            "filename": file.filename,
            "text": extracted_text,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        # Insert document into MongoDB (async)
        result = await resumes_collection.insert_one(resume_document)
        
        # Return success response
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Resume uploaded and stored successfully",
                "document_id": str(result.inserted_id),
                "company": company.strip(),
                "filename": file.filename,
                "uploaded_at": resume_document["uploaded_at"]
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/resumes")
async def get_resumes():
    """
    Get all resumes from MongoDB.
    Returns a list of all uploaded resumes (without the full text content).
    """
    try:
        db = await get_db()
        resumes_collection = db.resumes
        
        # Get all resumes (exclude the full text for listing)
        cursor = resumes_collection.find({}, {"text": 0})  # Exclude text field
        resumes = await cursor.to_list(length=100)
        
        # Convert ObjectId to string
        for resume in resumes:
            resume["_id"] = str(resume["_id"])
        
        return {
            "success": True,
            "count": len(resumes),
            "resumes": resumes
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching resumes: {str(e)}"
        )


@app.get("/resumes/{resume_id}")
async def get_resume(resume_id: str):
    """
    Get a specific resume by ID.
    Returns the full resume including extracted text.
    """
    try:
        from bson import ObjectId
        from bson.errors import InvalidId
        
        db = await get_db()
        resumes_collection = db.resumes
        
        try:
            resume = await resumes_collection.find_one({"_id": ObjectId(resume_id)})
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid resume ID format")
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        resume["_id"] = str(resume["_id"])
        
        return {
            "success": True,
            "resume": resume
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching resume: {str(e)}"
        )


@app.get("/view")
async def view_data():
    """
    View all uploaded documents in MongoDB.
    Returns all documents from the resumes collection.
    """
    db = await get_db()
    cursor = db.resumes.find()
    data = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        data.append(doc)
    return data
