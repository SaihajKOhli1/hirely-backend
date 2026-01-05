"""
FastAPI backend application.
"""
# Load environment variables FIRST, before any other imports that use them
from dotenv import load_dotenv
load_dotenv()

import os
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from db import get_db
from utils.extract_text import extract_text_from_pdf
from utils.scoring import score_resume_with_llm, PROMPT_VERSION

app = FastAPI(
    title="Hirely API",
    description="Backend API for Hirely",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """
    Verify required environment variables on startup.
    Supports both local and cloud Ollama instances, and Groq.
    """
    # Always required
    required_vars = {
        "MONGO_URI": "MongoDB connection URI is required for database operations"
    }
    
    # Check LLM provider
    llm_provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    if llm_provider == "groq":
        # Groq mode: require GROQ_API_KEY and GROQ_MODEL
        required_vars["GROQ_API_KEY"] = "Groq API key is required for Groq LLM provider"
        required_vars["GROQ_MODEL"] = "Groq model name is required for Groq LLM provider"
    else:
        # Ollama mode: require OLLAMA_BASE_URL and OLLAMA_MODEL
        required_vars["OLLAMA_BASE_URL"] = "Ollama base URL is required for resume scoring"
        required_vars["OLLAMA_MODEL"] = "Ollama model name is required for resume scoring"
        
        # Check if using local Ollama (no API key required for localhost)
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "").strip()
        is_local_ollama = ollama_base_url.startswith("http://localhost") or ollama_base_url.startswith("http://127.0.0.1")
        
        # OLLAMA_API_KEY is only required for cloud instances
        if not is_local_ollama:
            required_vars["OLLAMA_API_KEY"] = "Ollama API key is required for cloud Ollama instances"
    
    missing_vars = []
    for var_name, error_message in required_vars.items():
        value = os.getenv(var_name)
        if not value or not value.strip():
            missing_vars.append(var_name)
        else:
            # Safe logging: confirm variable is loaded without exposing the value
            print(f"✓ {var_name} loaded")
    
    if missing_vars:
        missing_list = ", ".join(missing_vars)
        raise RuntimeError(
            f"Missing required environment variables: {missing_list}. "
            "Please set these in your .env file or environment."
        )
    
    # Log active LLM provider and model
    if llm_provider == "groq":
        groq_model = os.getenv("GROQ_MODEL")
        print(f"✓ LLM_PROVIDER=groq, GROQ_MODEL={groq_model}")
    else:
        ollama_model = os.getenv("OLLAMA_MODEL")
        print(f"✓ LLM_PROVIDER=ollama, OLLAMA_MODEL={ollama_model}")
    
    # Log LLM provider and configuration
    if llm_provider == "groq":
        groq_model = os.getenv("GROQ_MODEL")
        print("✓ Running in GROQ MODE")
        print(f"✓ Groq configured with model: {groq_model}")
    else:
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "").strip()
        ollama_model = os.getenv("OLLAMA_MODEL")
        is_local_ollama = ollama_base_url.startswith("http://localhost") or ollama_base_url.startswith("http://127.0.0.1")
        if is_local_ollama:
            print("✓ Running in LOCAL OLLAMA MODE (no API key required)")
        else:
            print("✓ Running in CLOUD OLLAMA MODE (API key authenticated)")
        print(f"✓ Ollama configured: {ollama_base_url} with model {ollama_model}")
    
    db_name = os.getenv("DB_NAME", "hirely")
    print(f"✓ DB_NAME set to: {db_name}")


@app.get("/")
async def root():
    return {"status": "Hirely backend running"}

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow ALL origins (MVP / demo safe)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model for /score endpoint
class ScoreRequest(BaseModel):
    document_id: str
    company: str
    role: str



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


@app.post("/score")
async def score_resume(score_request: ScoreRequest = Body(...)):
    """
    Score an uploaded resume using LLM analysis.
    
    Args:
        score_request: JSON body with document_id, company, and role
        
    Returns:
        JSONResponse: Scoring result matching the required schema
        
    Raises:
        HTTPException: 400 for invalid input, 404 for missing resume, 502 for LLM errors
    """
    from bson import ObjectId
    from bson.errors import InvalidId
    
    # Validate input
    if not score_request.document_id or not score_request.document_id.strip():
        raise HTTPException(status_code=400, detail="document_id is required")
    if not score_request.company or not score_request.company.strip():
        raise HTTPException(status_code=400, detail="company is required")
    if not score_request.role or not score_request.role.strip():
        raise HTTPException(status_code=400, detail="role is required")
    
    try:
        # Get database
        db = await get_db()
        resumes_collection = db.resumes
        
        # Fetch resume document from MongoDB
        try:
            resume_doc = await resumes_collection.find_one({"_id": ObjectId(score_request.document_id)})
        except InvalidId:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document_id format: {score_request.document_id}"
            )
        
        if not resume_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Resume not found with document_id: {score_request.document_id}. Please upload the resume first using /upload."
            )
        
        # Get resume text
        resume_text = resume_doc.get("text")
        if not resume_text:
            raise HTTPException(
                status_code=404,
                detail=f"Resume text not found for document_id: {score_request.document_id}. The resume may not have been processed correctly."
            )
        
        # Score the resume using LLM
        try:
            scoring_result = await score_resume_with_llm(
                resume_text=resume_text,
                company=score_request.company.strip(),
                role=score_request.role.strip()
            )
        except ValueError as e:
            # JSON parsing errors or validation errors
            error_msg = str(e)
            if "JSON" in error_msg or "parse" in error_msg.lower():
                raise HTTPException(
                    status_code=502,
                    detail=f"LLM returned invalid JSON format. Debug info: {error_msg}"
                )
            else:
                # Check if it's a missing env var error
                if "OLLAMA_API_KEY" in error_msg or "OLLAMA_BASE_URL" in error_msg or "OLLAMA_MODEL" in error_msg:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Ollama configuration error: {error_msg}. Please check environment variables."
                    )
                raise HTTPException(status_code=500, detail=f"Scoring validation error: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            raise HTTPException(
                status_code=502,
                detail=f"LLM scoring error: {error_msg}"
            )
        
        # Store scoring result in MongoDB
        ai_score_data = {
            "overall_score": scoring_result["overall_score"],
            "metrics": scoring_result["metrics"],
            "missing_keywords": scoring_result["missing_keywords"],
            "strengths": scoring_result["strengths"],
            "top_fixes": scoring_result["top_fixes"],
            "section_feedback": scoring_result["section_feedback"],
            "notes": scoring_result["notes"],
            "model": os.getenv("OLLAMA_MODEL"),
            "provider": "ollama",
            "prompt_version": PROMPT_VERSION,
            "scored_at": datetime.utcnow().isoformat(),
            "company": score_request.company.strip(),
            "role": score_request.role.strip()
        }
        
        # Update the resume document with scoring results
        await resumes_collection.update_one(
            {"_id": ObjectId(score_request.document_id)},
            {"$set": {"ai_score": ai_score_data}}
        )
        
        # Return the scoring result
        return JSONResponse(
            status_code=200,
            content=scoring_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
